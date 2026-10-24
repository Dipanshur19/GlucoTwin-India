# Reproduce GlucoTwin India

## Environment
Use Python 3.12 and `requirements.txt`. CPU only. Training sets OpenMP and BLAS thread counts to two unless the user overrides them. No remote model service is used. Build-host elapsed time is stored in the summary; it is not a portable latency benchmark.

## Commands from the project directory
```bash
python -m pip install -r requirements.txt
python -m glucotwin.prepare
python -m glucotwin.train
python -m unittest discover -s tests -v
python app.py
```
`prepare` extracts the included, attributed source CSV archive into a temporary directory and rebuilds processed records. `train` overwrites model/results artifacts using the fixed participant split. Small floating-point differences can occur across platforms.

## Evaluation integrity
Validation selects fused/adaptive variants and the episode-score threshold. Calibration determines interval radii. Test data only estimate final performance. All partitions are disjoint by participant, so overlapping windows cannot cross participant partitions. Training is sampled every fifteen minutes; evaluation is every five minutes. Each training participant is equally weighted before classifier class balancing. Test headline errors are patient-macro means, not pooled-row means.

At issue time t, current dynamic inputs represent observations at least fifteen minutes old. Features use trailing windows, forward decay and no future fill. A horizon h forecast can only update residual memory after h+15 minutes. Unit tests compare whole-trace predictions against predictions recomputed from a prefix; changing future inputs must leave earlier features unchanged.

Episode scoring matches at most one future onset to each issued alert and applies a sixty-minute cooldown. A qualifying onset needs the full three-bin event inside the forecast window. Only onsets with an eligible prior warning opportunity are counted as observable. False alerts are normalized by eligible monitored time, not raw study duration. These definitions should be retained in comparisons.

## Included audit files
- `data/audit.json`: source and retained coverage for each person.
- `data/source_manifest.json`: original CSV SHA-256 values.
- `data/split.json`: exact participant partition and seed.
- `results/per_patient_metrics.csv`: patient/horizon/model errors.
- `results/forecast_metrics.csv`: patient-macro aggregate errors.
- `results/summary.json`: alert counts, intervals and runtime.
- `results/validation_thresholds.json`: validation-only threshold search.
- `tests/test_core.py`: twelve functional and causality tests.

## App constraints
Localhost-only research server; no authentication and no deployment hardening. Keep it local. No arbitrary joblib upload is exposed. Future data are hidden by default and only shown through an explicit retrospective reveal control. Synthetic scenario curves are not model forecasts.
