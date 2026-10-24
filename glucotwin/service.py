"""Local inference service. Models are trusted bundled artifacts only."""
import json,pathlib,time
from functools import lru_cache
import numpy as np
import pandas as pd
import joblib
from .core import features,eligible,SENSOR,FUSED,HORIZONS,delayed_adaptation,scenario_curve

ROOT=pathlib.Path(__file__).resolve().parents[1]
class TwinService:
    def __init__(self,root=ROOT):
        self.root=pathlib.Path(root)
        self.bundle=joblib.load(self.root/'models/glucotwin.joblib')
        self.profiles={p['id']:p for p in json.loads((self.root/'data/profiles.json').read_text())}
        self.summary=json.loads((self.root/'results/summary.json').read_text())
        self.metrics=pd.read_csv(self.root/'results/forecast_metrics.csv').replace({np.nan:None}).to_dict('records')
    @lru_cache(maxsize=8)
    def patient(self,pid):
        if pid not in self.bundle['split']['test']:raise ValueError('Choose a bundled test participant')
        return pd.read_csv(self.root/f'data/patient_{pid:03}.csv.gz')
    def metadata(self):
        pts=[]
        for pid in self.bundle['split']['test']:
            d=self.patient(pid);cache=pd.read_csv(self.root/f'results/replay_{pid:03}.csv.gz')
            valid=eligible(d)&(d.glucose<=180)&cache.event_probability.notna()
            selected=int(cache.loc[valid,'event_probability'].idxmax()) if valid.any() else 350
            pts.append({**self.profiles[pid],'rows':len(d),'start':d.timestamp.iloc[0],'default_index':selected})
        return {'patients':pts,'summary':self.summary,'metrics':self.metrics}
    @lru_cache(maxsize=8)
    def predictions(self,pid):
        d=self.patient(pid);x=features(d,self.profiles[pid]);out={}
        for h in HORIZONS:
            base=np.clip(d.glucose.to_numpy()+self.bundle['models'][f'fused_{h}'].predict(x[FUSED]),40,400)
            p,state=delayed_adaptation(base,d.glucose,h)
            out[h]=p if self.bundle['selected'][h]=='adaptive' else base
            out[f'state_{h}']=state
        out['score']=self.bundle['event_model'].predict_proba(x[FUSED])[:,1]
        return out
    def snapshot(self,pid,index,outage=False,reveal=False):
        start=time.perf_counter();d=self.patient(pid)
        if index<288 or index>=len(d)-25:raise ValueError('Index must leave 24 h warm-up and 2 h of replay')
        out=self.predictions(pid);r=d.iloc[index];ok=bool(eligible(d).iloc[index]) and not outage
        g=float(r.glucose) if np.isfinite(r.glucose) else None
        score=float(out['score'][index]) if ok else None
        forecast=[]
        for h in HORIZONS:
            point=float(out[h][index]);radius=self.bundle['radii'][h]
            forecast.append({'minutes':h,'value':point if ok else None,'low':max(40,point-radius) if ok else None,'high':min(400,point+radius) if ok else None,
                             'method':self.bundle['selected'][h],'correction':float(out[f'state_{h}'][index]) if ok else None})
        begin=max(0,index-36)
        history=[{'minutes':(j-index)*5-15,'value':float(d.glucose.iloc[j]) if np.isfinite(d.glucose.iloc[j]) else None} for j in range(begin,index+1)]
        future=[]
        if reveal:
            future=[{'minutes':(j-index)*5,'value':float(d.truth.iloc[j]) if np.isfinite(d.truth.iloc[j]) else None} for j in range(index,min(len(d),index+25))]
        status='INSUFFICIENT DATA' if not ok else ('HIGH AT LAST READING' if g>180 else ('REVIEW FORECAST' if score>=self.bundle['alert_threshold'] else 'MONITOR'))
        f=features(d.iloc[:index+1],self.profiles[pid]).iloc[-1]
        return {'patient':self.profiles[pid],'index':index,'timestamp':r.timestamp,'current':g,'valid':ok,'outage':outage,'sensor_age':int(r.sensor_age) if not outage else 45,
                'status':status,'score':score,'threshold':self.bundle['alert_threshold'],'forecast':forecast,'history':history,'future':future,
                'context':{'recent_slope':float(f.slope30) if np.isfinite(f.slope30) else None,'carb_load':float(f.carb_load),'activity':float(f.met30) if np.isfinite(f.met30) else None},
                'latency_ms':(time.perf_counter()-start)*1000,
                'warning':'Research prototype. No diagnosis, dosing or treatment recommendation. Replay from a US cohort.'}

def clean_json(value):
    if isinstance(value,dict):return {str(k):clean_json(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [clean_json(v) for v in value]
    if isinstance(value,(float,np.floating)) and not np.isfinite(value):return None
    if isinstance(value,np.generic):return value.item()
    return value
