import json,pathlib,unittest
import numpy as np
import pandas as pd
from glucotwin.core import features,delayed_adaptation,episode_labels,eligible,scenario_curve
from glucotwin.service import TwinService,ROOT

class CausalityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service=TwinService();cls.pid=cls.service.bundle['split']['test'][0]
        cls.frame=cls.service.patient(cls.pid);cls.profile=cls.service.profiles[cls.pid]
    def test_patient_partitions_disjoint(self):
        s=self.service.bundle['split'];sets=[set(s[k]) for k in ['train','validation','calibration','test']]
        for i,a in enumerate(sets):
            for b in sets[i+1:]:self.assertFalse(a&b)
        self.assertEqual(len(set.union(*sets)),45)
    def test_features_prefix_invariant(self):
        full=features(self.frame,self.profile)
        for n in [350,700,1200]:
            np.testing.assert_allclose(full.iloc[n-1],features(self.frame.iloc[:n],self.profile).iloc[-1],equal_nan=True)
    def test_future_changes_do_not_change_features(self):
        d=self.frame.copy();d.loc[701:,'glucose']=350;d.loc[701:,'carbs']=200
        np.testing.assert_allclose(features(self.frame,self.profile).iloc[:701],features(d,self.profile).iloc[:701],equal_nan=True)
    def test_adaptation_waits_for_observable_outcome(self):
        base=np.full(100,100.);observed=np.full(100,130.)
        a,state=delayed_adaptation(base,observed,60,observation_delay=15)
        self.assertTrue(np.all(state[:15]==0));self.assertGreater(state[15],0)
        changed=observed.copy();changed[70:]=300
        b,_=delayed_adaptation(base,changed,60)
        np.testing.assert_equal(a[:70],b[:70])
    def test_episode_requires_future_new_onset(self):
        g=np.full(30,100.);g[6:9]=200
        self.assertEqual(episode_labels(g)[0],1)
        g[:]=200;self.assertEqual(episode_labels(g)[0],0)
    def test_short_spike_is_not_sustained_episode(self):
        g=np.full(30,100.);g[6:8]=200;self.assertEqual(episode_labels(g)[0],0)
    def test_missing_future_is_unscorable(self):
        g=np.full(30,100.);g[6]=np.nan;self.assertTrue(np.isnan(episode_labels(g)[0]))
    def test_outage_suppresses_all_predictions(self):
        x=self.service.snapshot(self.pid,500,outage=True)
        self.assertFalse(x['valid']);self.assertIsNone(x['score'])
        self.assertTrue(all(f['value'] is None for f in x['forecast']))
    def test_future_hidden_by_default(self):
        self.assertEqual(self.service.snapshot(self.pid,500)['future'],[])
        self.assertTrue(self.service.snapshot(self.pid,500,reveal=True)['future'])
    def test_invalid_patient_and_row(self):
        with self.assertRaises(ValueError):self.service.patient(-1)
        with self.assertRaises(ValueError):self.service.snapshot(self.pid,0)
    def test_model_prediction_matches_prefix_recomputation(self):
        from glucotwin.core import FUSED
        d=self.frame.iloc[:701];x=features(d,self.profile)
        for h in [30,60,120]:
            base=np.clip(d.glucose.to_numpy()+self.service.bundle['models'][f'fused_{h}'].predict(x[FUSED]),40,400)
            adapt,_=delayed_adaptation(base,d.glucose,h)
            actual=adapt if self.service.bundle['selected'][h]=='adaptive' else base
            np.testing.assert_allclose(self.service.predictions(self.pid)[h][:701],actual,equal_nan=True)
    def test_synthetic_scenario_bounded_and_starts_at_baseline(self):
        t,g=scenario_curve(120,carbs=50,activity=10)
        self.assertEqual(g[0],120);self.assertTrue(np.all((g>=40)&(g<=400)));self.assertEqual(t[-1],120)

if __name__=='__main__':unittest.main()
