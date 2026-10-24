"""Train, tune, calibrate and evaluate on four disjoint patient partitions."""
import os
os.environ.setdefault('OMP_NUM_THREADS','2')
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
import json,pathlib,time,gzip,io
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingRegressor,HistGradientBoostingClassifier
from sklearn.metrics import mean_absolute_error,mean_squared_error,average_precision_score,roc_auc_score,brier_score_loss,precision_score,recall_score
from .core import HORIZONS,SENSOR,FUSED,features,eligible,delayed_adaptation,episode_labels,alert_episodes

ROOT=pathlib.Path(__file__).resolve().parents[1]

def run(root=ROOT):
    started=time.perf_counter();profiles=json.loads((root/'data/profiles.json').read_text());split=json.loads((root/'data/split.json').read_text())
    patients={p['id']:p for p in profiles};frames={};xs={};valids={};labels={}
    for pid,p in patients.items():
        d=pd.read_csv(root/f'data/patient_{pid:03}.csv.gz');frames[pid]=d
        xs[pid]=features(d,p);valids[pid]=eligible(d).to_numpy();labels[pid]=episode_labels(d.truth)
    def xy(ids,cols,h=None,event=False,stride=1):
        xx=[];yy=[];weights=[]
        for pid in ids:
            d=frames[pid];y=labels[pid] if event else d.truth.shift(-h//5).to_numpy()-d.glucose.to_numpy()
            ok=valids[pid]&np.isfinite(y)
            if event:ok &= d.glucose.to_numpy()<=180
            ok &= np.arange(len(d))%stride==0
            xx.append(xs[pid].loc[ok,cols]);yy.append(y[ok])
            # Equal patient weight prevents long traces dominating.
            weights.append(np.full(ok.sum(),1/max(1,ok.sum())))
        w=np.concatenate(weights);w=w/w.mean()
        return pd.concat(xx,ignore_index=True),np.concatenate(yy),w
    bundle={'version':'1.0.0','horizons':HORIZONS,'models':{},'selected':{},'radii':{},'features':FUSED,'split':split}
    preds={pid:{} for pid in patients};rows=[];val_scores={}
    for h in HORIZONS:
        for name,cols in [('sensor',SENSOR),('fused',FUSED)]:
            x,y,w=xy(split['train'],cols,h=h,stride=3)
            model=HistGradientBoostingRegressor(max_iter=180,max_leaf_nodes=15,learning_rate=.06,l2_regularization=12,min_samples_leaf=35,early_stopping=False,random_state=2026)
            model.fit(x,y,sample_weight=w);bundle['models'][f'{name}_{h}']=model
            for pid,d in frames.items():
                raw=np.clip(d.glucose.to_numpy()+model.predict(xs[pid][cols]),40,400)
                preds[pid][f'{name}_{h}']=raw
                if name=='fused':
                    adapted,state=delayed_adaptation(raw,d.glucose,h)
                    preds[pid][f'adaptive_{h}']=adapted
                    preds[pid][f'state_{h}']=state
            print('trained',name,h,'windows',len(y),flush=True)
        for pid,d in frames.items():preds[pid][f'persistence_{h}']=d.glucose.to_numpy()
        # Selection on validation ONLY; persistence remains an eligible winner.
        candidates=['persistence','sensor','fused','adaptive']
        def errors(ids,name):
            ret=[]
            for pid in ids:
                d=frames[pid];y=d.truth.shift(-h//5).to_numpy();pred=preds[pid][f'{name}_{h}']
                ok=valids[pid]&np.isfinite(y)&np.isfinite(pred)
                ret.append(np.abs(y[ok]-pred[ok]))
            return ret
        scores={n:float(np.mean([np.mean(e) for e in errors(split['validation'],n) if len(e)])) for n in candidates}
        # Deploy a fused twin, selected between fused and adaptive on validation;
        # all baselines are reported even if they outperform this constrained choice.
        chosen=min(['fused','adaptive'],key=lambda n:scores[n]);bundle['selected'][h]=chosen;val_scores[h]=scores
        residuals=np.concatenate(errors(split['calibration'],chosen))
        q=min(1,np.ceil((len(residuals)+1)*.9)/max(1,len(residuals)))
        radius=float(np.quantile(residuals,q,method='higher'));bundle['radii'][h]=radius
        for name in candidates:
            for pid in split['test']:
                d=frames[pid];truth=d.truth.shift(-h//5).to_numpy();p=preds[pid][f'{name}_{h}'];ok=valids[pid]&np.isfinite(truth)&np.isfinite(p)
                rows.append({'horizon':h,'model':name,'patient':pid,'windows':int(ok.sum()),'mae':float(mean_absolute_error(truth[ok],p[ok])),
                    'rmse':float(np.sqrt(mean_squared_error(truth[ok],p[ok]))),
                    'coverage90':float(np.mean(np.abs(truth[ok]-p[ok])<=radius)) if name==chosen else None})
    # New episode onset classifier. Fixed class balancing; threshold tuned on val.
    x,y,w=xy(split['train'],FUSED,event=True,stride=3)
    classifier=HistGradientBoostingClassifier(max_iter=160,max_leaf_nodes=12,learning_rate=.05,l2_regularization=15,min_samples_leaf=40,class_weight='balanced',early_stopping=False,random_state=2026)
    classifier.fit(x,y,sample_weight=w);bundle['event_model']=classifier
    for pid in patients:preds[pid]['event_probability']=classifier.predict_proba(xs[pid])[:,1]
    threshold_scores=[]
    for threshold in np.arange(.1,.91,.05):
        events=[]
        for pid in split['validation']:
            ok=valids[pid]&np.isfinite(labels[pid]);events.append(alert_episodes(frames[pid],preds[pid]['event_probability'],float(threshold),ok))
        tp=sum(e['true_alerts'] for e in events);al=sum(e['alerts'] for e in events);n=sum(e['observable_onsets'] for e in events)
        precision=tp/max(1,al);recall=tp/max(1,n);f1=2*precision*recall/max(1e-9,precision+recall)
        threshold_scores.append({'threshold':float(threshold),'f1':f1,'precision':precision,'recall':recall})
    best=max(threshold_scores,key=lambda r:(r['f1'],r['threshold']));bundle['alert_threshold']=best['threshold']
    ev=[];all_y=[];all_p=[]
    for pid in split['test']:
        ok=valids[pid]&np.isfinite(labels[pid]);e=alert_episodes(frames[pid],preds[pid]['event_probability'],best['threshold'],ok);e['patient']=pid;ev.append(e)
        ok &= frames[pid].glucose.to_numpy()<=180
        all_y.extend(labels[pid][ok]);all_p.extend(preds[pid]['event_probability'][ok])
    ay=np.asarray(all_y);ap=np.asarray(all_p);tp=sum(e['true_alerts'] for e in ev);al=sum(e['alerts'] for e in ev);n=sum(e['observable_onsets'] for e in ev);days=sum(e['eligible_days'] for e in ev);leads=sum([e['lead_minutes'] for e in ev],[])
    event_summary={'threshold':best['threshold'],'alerts':al,'true_alerts':tp,'false_alerts':al-tp,'observable_onsets':n,'detected_onsets':sum(e['detected_onsets'] for e in ev),
        'episode_precision':tp/max(1,al),'episode_recall':sum(e['detected_onsets'] for e in ev)/max(1,n),'false_alerts_per_day':(al-tp)/max(days,1e-9),
        'median_lead_minutes':float(np.median(leads)) if leads else None,'eligible_patient_days':days,
        'window_auprc':float(average_precision_score(ay,ap)),'window_prevalence':float(ay.mean()),'window_brier':float(brier_score_loss(ay,ap)),
        'window_auroc':float(roc_auc_score(ay,ap)) if len(np.unique(ay))>1 else None,
        'score_note':'Uncalibrated ranking score; class weighting means it must not be interpreted as a clinical probability.'}
    out=pd.DataFrame(rows);out.to_csv(root/'results/per_patient_metrics.csv',index=False)
    summary=out.groupby(['horizon','model']).agg(mae=('mae','mean'),rmse=('rmse','mean'),windows=('windows','sum'),coverage90=('coverage90','mean')).reset_index()
    summary.to_csv(root/'results/forecast_metrics.csv',index=False)
    # Patient-cluster bootstrap on MAE differences; very small test cohort disclosed.
    rng=np.random.default_rng(2026);boot={}
    for h in HORIZONS:
        a=out[(out.horizon==h)&(out.model=='persistence')].set_index('patient').mae
        b=out[(out.horizon==h)&(out.model==bundle['selected'][h])].set_index('patient').mae
        dif=(a-b).to_numpy();draw=rng.choice(dif,(5000,len(dif)),replace=True).mean(axis=1)
        boot[h]={'mae_improvement':float(dif.mean()),'ci95':[float(v) for v in np.quantile(draw,[.025,.975])]}
    result={'split':split,'selected':bundle['selected'],'interval_radius':bundle['radii'],'validation_mae':val_scores,'events':event_summary,'event_patients':ev,
            'patient_bootstrap':boot,'training_seconds':time.perf_counter()-started,'train_participants':len(split['train']),'test_participants':len(split['test']),
            'model_note':'Adaptive data-driven partial twin. No validated physiological or causal treatment model.'}
    (root/'results/summary.json').write_text(json.dumps(result,indent=2));(root/'results/validation_thresholds.json').write_text(json.dumps(threshold_scores,indent=2))
    buffer=io.BytesIO();joblib.dump(bundle,buffer,compress=3);(root/'models/glucotwin.joblib').write_bytes(buffer.getvalue())
    # Replay caches contain causal inputs and per-row predictions; truth is separate.
    for pid in split['test']:
        d=frames[pid].copy();d['eligible']=valids[pid]
        for name,values in preds[pid].items():d[name]=values
        (root/f'results/replay_{pid:03}.csv.gz').write_bytes(gzip.compress(d.to_csv(index=False,float_format='%.5f').encode(),mtime=0))
    print(summary.to_string(index=False));print(json.dumps(event_summary,indent=2));print('seconds',result['training_seconds'])
    return result
if __name__=='__main__':run()
