"""Causal features, delayed feedback and episode definitions.

All time axes use five-minute grid indices. A forecast at row i can only
adapt from an error whose target is observed by i. Clinical use is excluded.
"""
import numpy as np
import pandas as pd

HORIZONS = (30, 60, 120)
STATIC = ['age', 'female', 'bmi', 'hba1c', 'fasting_glucose']
SENSOR = ['glucose','lag15','lag30','lag60','lag120','slope15','slope30',
          'mean30','mean60','std30','range60','ewm60','hour_sin','hour_cos',
          'hr30','met30','met120','sensor_age','missing30']
CONTEXT = ['carb_load','protein_load','fat_load','minutes_since_meal']
FUSED = SENSOR + CONTEXT + STATIC

def decay_state(values, tau_minutes):
    result=np.zeros(len(values),dtype=float); state=0.
    for i,v in enumerate(np.nan_to_num(values,nan=0.)):
        state=state*np.exp(-5/tau_minutes)+max(0,float(v));result[i]=state
    return result

def features(frame, profile):
    """Prefix invariant: no centered windows, interpolation or backfill."""
    g=frame['glucose'].astype(float)
    f=pd.DataFrame(index=frame.index)
    f['glucose']=g
    for minutes in (15,30,60,120):f[f'lag{minutes}']=g.shift(minutes//5)
    f['slope15']=(g-g.shift(3))/15
    f['slope30']=(g-g.shift(6))/30
    for minutes in (30,60):f[f'mean{minutes}']=g.rolling(minutes//5,min_periods=3).mean()
    f['std30']=g.rolling(6,min_periods=3).std()
    f['range60']=g.rolling(12,min_periods=3).max()-g.rolling(12,min_periods=3).min()
    f['ewm60']=g.ewm(halflife=12,adjust=False).mean()
    ts=pd.to_datetime(frame['timestamp']);hour=ts.dt.hour+ts.dt.minute/60
    f['hour_sin']=np.sin(hour*2*np.pi/24);f['hour_cos']=np.cos(hour*2*np.pi/24)
    f['hr30']=frame.hr.rolling(6,min_periods=1).mean()
    f['met30']=frame.met.rolling(6,min_periods=1).mean()
    f['met120']=frame.met.rolling(24,min_periods=1).mean()
    f['sensor_age']=frame.sensor_age
    f['missing30']=g.isna().rolling(6,min_periods=1).mean()
    for col,tau in [('carbs',60),('protein',120),('fat',180)]:
        name={'carbs':'carb_load','protein':'protein_load','fat':'fat_load'}[col]
        f[name]=decay_state(frame[col].to_numpy(),tau)
    last=-10000;elapsed=[]
    for i,v in enumerate(frame.carbs.fillna(0)):
        if v>0:last=i
        elapsed.append(min(1440,(i-last)*5))
    f['minutes_since_meal']=elapsed
    for col in STATIC:f[col]=float(profile.get(col,np.nan))
    return f[FUSED].replace([np.inf,-np.inf],np.nan)

def eligible(frame):
    return (frame.glucose.notna() & (frame.sensor_age<=20) &
            (frame.glucose.rolling(24,min_periods=1).count()>=18) &
            (np.arange(len(frame))>=288))

def delayed_adaptation(base, observed, horizon, gain=0.35, observation_delay=15):
    """Update from matured forecast errors; fixed gain set before test."""
    base=np.asarray(base,dtype=float);g=np.asarray(observed,dtype=float)
    steps=(horizon+observation_delay)//5;state=0.;pred=np.array(base,copy=True);states=np.zeros(len(base))
    for i in range(len(base)):
        j=i-steps
        if j>=0 and np.isfinite(g[i]) and np.isfinite(base[j]):
            residual=np.clip(g[i]-base[j],-60,60)
            state=.97*state+.03*residual
        states[i]=gain*state
        pred[i]=np.clip(base[i]+states[i],40,400)
    return pred,states

def episode_labels(glucose,horizon=60):
    """New onset above 180 for 3 grid points within horizon, ending <= horizon.

    Three points cover three five-minute bins. An onset must be in the future;
    all future bins must be present. This is an engineering endpoint.
    """
    g=np.asarray(glucose,dtype=float);steps=horizon//5
    out=np.full(len(g),np.nan)
    for i in range(len(g)-steps):
        future=g[i+1:i+steps+1]
        if not np.isfinite(g[i]) or not np.isfinite(future).all():continue
        out[i]=float(any(g[j-1]<=180 and np.all(g[j:j+3]>180) for j in range(i+1,i+steps-1)))
    return out

def onsets(glucose):
    g=np.asarray(glucose,dtype=float);result=[]
    for j in range(1,len(g)-2):
        if np.isfinite(g[j-1:j+3]).all() and g[j-1]<=180 and np.all(g[j:j+3]>180):result.append(j)
    return result

def alert_episodes(frame,probabilities,threshold,valid):
    """One alert per 60 minutes; match at most one future onset per alert."""
    g=frame.glucose.to_numpy();ons=onsets(frame.truth);alerts=[];last=-10000
    for i,p in enumerate(probabilities):
        if valid[i] and g[i]<=180 and p>=threshold and i-last>=12:
            alerts.append(i);last=i
    observable=[j for j in ons if any(valid[max(0,j-10):j] & (g[max(0,j-10):j]<=180))]
    matched=set();true_alerts=0;leads=[]
    for i in alerts:
        # The full three-bin episode must be visible within 60 minutes.
        candidates=[j for j in observable if i<j and j+2<=i+12 and j not in matched]
        if candidates:
            j=min(candidates);matched.add(j);true_alerts+=1;leads.append((j-i)*5)
    days=float(np.sum(valid))*5/1440
    return {'alerts':len(alerts),'true_alerts':true_alerts,'false_alerts':len(alerts)-true_alerts,
            'observable_onsets':len(observable),'detected_onsets':len(matched),
            'lead_minutes':leads,'eligible_days':days}

def scenario_curve(glucose,carbs=45,activity=0,gain=0.8):
    """Illustrative response assumption, never a causal treatment estimate."""
    t=np.arange(0,125,5,dtype=float)
    meal=gain*carbs*(t/45)*np.exp(1-t/45)
    movement=0.15*activity*(1-np.exp(-t/60))
    return t,np.clip(glucose+meal-movement,40,400)
