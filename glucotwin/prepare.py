"""Prepare the openly licensed CGMacros CSVs without adding interpolation."""
import argparse,hashlib,json,pathlib,zipfile,gzip
import numpy as np
import pandas as pd

ROOT=pathlib.Path(__file__).resolve().parents[1]
def prepare(raw_dir,root=ROOT):
    raw_dir=pathlib.Path(raw_dir);data=root/'data';data.mkdir(exist_ok=True)
    bio=pd.read_csv(raw_dir/'bio.csv');profiles=[];audits=[];manifest=[]
    for _,row in bio.iterrows():
        pid=int(row['subject']);source=raw_dir/f'CGMacros-{pid:03}.csv'
        if not source.exists():continue
        p={'id':pid,'age':int(row.Age),'female':int(str(row.Gender).upper()=='F'),
           'bmi':float(row.BMI),'hba1c':float(row['A1c PDL (Lab)']),
           'fasting_glucose':float(row['Fasting GLU - PDL (Lab)'])}
        p['cohort']='T2D' if p['hba1c']>6.4 else ('Prediabetes' if p['hba1c']>=5.7 else 'Normoglycemia')
        d=pd.read_csv(source);d.columns=d.columns.str.strip();d=d.rename(columns={c:'METs' for c in d.columns if c.lower()=='mets'});d['timestamp']=pd.to_datetime(d.Timestamp)
        d=d.set_index('timestamp').sort_index();d=d[~d.index.duplicated(keep='last')]
        # Original study uses five-minute Dexcom. Retain the initial observed
        # phase and integer values only; discard fractional interpolated rows.
        first=d['Dexcom GL'].first_valid_index()
        if first is None:continue
        candidate=((d.index-first).total_seconds()%300==0)
        integer=np.isclose(d['Dexcom GL'],np.round(d['Dexcom GL']),equal_nan=False)
        values=d['Dexcom GL'].where(candidate & integer).where(lambda s:s.between(40,400))
        truth=values.resample('5min',closed='right',label='right').last()
        f=pd.DataFrame({'truth':truth})
        f['glucose']=truth.shift(3).ffill(limit=1)
        # Every feature reading is at least 15 minutes old, including meal logs.
        for target,source_col in [('hr','HR'),('met','METs')]:
            series=d[source_col] if source_col in d else pd.Series(np.nan,index=d.index)
            f[target]=pd.to_numeric(series,errors='coerce').resample('5min',closed='right',label='right').mean().shift(3)
        f['met']=f.met/10
        for target,source_col in [('carbs','Carbs'),('protein','Protein'),('fat','Fat')]:
            f[target]=pd.to_numeric(d[source_col],errors='coerce').fillna(0).resample('5min',closed='right',label='right').sum().shift(3).fillna(0)
        f['sensor_age']=np.where(truth.shift(3).notna(),15,np.where(truth.shift(4).notna(),20,999))
        f.index.name='timestamp';f=f.reset_index()
        (data/f'patient_{pid:03}.csv.gz').write_bytes(gzip.compress(f.to_csv(index=False,float_format='%.5f').encode(),mtime=0))
        profiles.append(p)
        audits.append({'id':pid,'rows':len(f),'truth_coverage':float(f.truth.notna().mean()),
                       'retained_phase_fraction':float((candidate & integer).sum()/max(1,candidate.sum())),
                       'source_first':str(d.index.min()),'source_last':str(d.index.max())})
        manifest.append({'file':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
    ids=sorted(p['id'] for p in profiles if p['cohort']=='T2D')
    rng=np.random.default_rng(2026);permuted=list(map(int,rng.permutation(ids)))
    test=permuted[:3];calibration=permuted[3:6];validation=permuted[6:9]
    train=sorted(p['id'] for p in profiles if p['id'] not in test+calibration+validation)
    split={'seed':2026,'train':train,'validation':validation,'calibration':calibration,'test':test,
           'policy':'Patient-disjoint; validation chooses model; calibration fits interval radii; test locked. First 24 h warm-up excluded from scored windows.'}
    for name,obj in [('profiles.json',profiles),('audit.json',audits),('split.json',split),('source_manifest.json',manifest)]:
        (data/name).write_text(json.dumps(obj,indent=2))
    print(json.dumps({'patients':len(profiles),'t2d':len(ids),'split':split,'median_truth_coverage':float(np.median([a['truth_coverage'] for a in audits]))},indent=2))
    return profiles,split

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--raw-dir');args=ap.parse_args()
    if args.raw_dir:prepare(args.raw_dir)
    else:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(ROOT/'data/source_csv.zip') as z:
                for n in z.namelist():
                    if pathlib.Path(n).name!=n:raise ValueError('Unsafe source archive')
                z.extractall(tmp)
            prepare(tmp)
