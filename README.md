# GlucoTwin India
## An adaptive partial Digital Twin for glucose forecasting

**Digital Twin Challenge 2026 · Happiest Health**  
**Team product · Indian Institute of Technology Kanpur**  
**Team leader and registered member: Dipanshu Raj** · [GitHub](https://github.com/Dipanshur19)

GlucoTwin joins the same participant's baseline clinical profile with glucose, wearable activity and recorded-meal streams. A patient-specific state updates as measurements arrive. The prototype forecasts glucose at 30, 60 and 120 minutes, estimates forecast uncertainty, and produces an exploratory review flag for a new high-glucose episode.

**Research prototype only.** These are retrospective results from a small US cohort. No Indian clinical validation, diagnosis, dosing, treatment benefit, regulatory approval or live wearable integration is claimed.

## Submission navigation

- [Presentation PDF](docs/GlucoTwin_Presentation.pdf) · [Editable PowerPoint](docs/GlucoTwin_Presentation.pptx)
- [Architecture PDF](docs/GlucoTwin_Architecture.pdf)
- [Technical report](docs/GlucoTwin_Technical_Report.pdf)
- [20-minute demo script](docs/Demo_Script.md) · [Video upload details](docs/DEMO_VIDEO.md)
- [Measured results](results/forecast_metrics.csv) · [Evaluation summary](results/summary.json)
- [Model card](MODEL_CARD.md) · [Data sources and licenses](DATA_SOURCES.md)
- [Reproduce the results](REPRODUCIBILITY.md) · [Jury questions](docs/Jury_QA.md)

## Demo video — required before submission

<!-- VIDEO_LINK_START -->
**Unlisted YouTube URL pending upload.** The supplied 20-minute MP4 must be uploaded as an unlisted YouTube video and linked here before submitting. The script below inserts the real link; no video URL is fabricated.
<!-- VIDEO_LINK_END -->

After uploading the supplied MP4:
```bash
python scripts/finalize_submission.py --video-url "YOUR_REAL_UNLISTED_YOUTUBE_URL" --repo-url "YOUR_REAL_PUBLIC_GITHUB_URL"
```
Run `python scripts/check_submission.py` to verify the local package. You must separately test both external URLs in a signed-out browser.

## Problem statement and healthcare use case

Adults with Type 2 diabetes may experience glucose excursions between periodic reviews. This proof-of-concept investigates whether paired baseline labs and sensor history can support patient-specific forecasting and a clinician review workflow.

Primary task: forecast glucose 60 minutes from the issue timestamp; 30 and 120 minutes are secondary horizons. The input stream is deliberately delayed by 15 minutes. An exploratory event endpoint is a **new crossing above 180 mg/dL followed by three consecutive five-minute bins above 180**, with all three bins inside the next 60 minutes. This is a study endpoint, not an emergency threshold or a patient-specific treatment target.

## Quick start — Python 3.12

Extract the complete project folder. Keep `models/`, `data/`, `results/` and `web/` beside `app.py`.

Windows: double-click `start_windows.bat` after installing Python 3.12.  
macOS/Linux: run `bash start.sh`.

Or use a terminal:
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:8765` if the browser does not open automatically. First-time dependency installation needs internet. The packaged data, model and dashboard work offline afterwards. No API key, GPU or paid service is required.

## Prototype walkthrough

1. Select a held-out study participant and inspect the clinical profile.
2. Step forward or play the historical sensor replay.
3. Review the three forecast horizons, nominal 90% intervals and ranking score.
4. Toggle **Reveal observed future** to inspect a retrospective prediction. The default view hides it.
5. Simulate a sensor outage: all forecasts and the risk score are withheld.
6. Open **Evidence** to compare all baselines and see alert limitations.
7. Open **Scenario sandbox** for an explicitly synthetic response illustration. Its assumed effects are not treatment predictions.
8. Export a JSON review record. No real-world patient data are collected or transmitted.

## Technical stack and AI/ML framework

Python 3.12, NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0, scikit-learn 1.8.0 and joblib 1.5.3. The frontend is dependency-free HTML/CSS/JavaScript with Canvas charts; a standard-library Python server binds only to localhost.

Three histogram gradient-boosting regressors predict glucose changes, using clinical context and causal sensor/meal features. Decaying meal states and rolling glucose/activity summaries evolve with each measurement. A bounded exponentially weighted residual correction personalizes each horizon using only errors whose outcomes are already observable. A separate gradient-boosting classifier ranks the risk of a future episode. Its class-weighted score is **not a calibrated probability**.

Validation patients select between fused and adaptive variants and choose the alert threshold. Separate calibration patients determine empirical 90% residual intervals. The final test patients do not select models, thresholds or interval widths. The deployed variant was adaptive at all three horizons.

## Measured outcomes

Patient-macro errors, mg/dL. Final test: **3 unseen T2D participants**, after a 24-hour warm-up. Training uses 36 participants, with 3 separate validation and 3 separate calibration participants.

| Horizon | Persistence MAE | Sensor-only MAE | Fused MAE | Adaptive MAE | Adaptive vs persistence |
|---|---:|---:|---:|---:|---:|
| 30 min | 19.74 | 21.22 | 20.34 | 18.48 | 6.4% lower |
| 60 min | 26.67 | 29.26 | 26.88 | 24.12 | 9.6% lower |
| 120 min | 35.26 | 35.86 | 33.41 | 29.00 | 17.7% lower |

At 60 minutes, nominal 90% intervals achieved **89.8%** patient-macro test coverage. This is empirical coverage on this test set, not a prospective guarantee.

Exploratory alerts: **14/64 alerts matched an upcoming onset**, **14/66 observable onsets detected**, **1.87 false alerts per eligible patient-day**, and **15 minutes median lead time** among matched alerts. These alert results are not adequate for clinical deployment. A 60-minute horizon must not be described as 60 minutes of demonstrated warning.

Training elapsed time on the build host: 26.8 seconds with two OpenMP threads. This is a host-specific measurement, not a performance promise. Detailed per-patient results, bootstrap intervals and raw counts are included.

## Data fusion and provenance

CGMacros v1.0.0 includes 45 participants, 14 in the study's T2D group. The same participant identifier joins demographics/labs and sensor records. Baseline fields are represented as an EHR-like clinical profile; no hospital EHR connection is implemented. No unrelated Synthea records are attached to real sensor traces.

The source already interpolates glucose to one-minute rows. We retain initial-cadence-compatible integer Dexcom readings, avoid adding interpolation or backward fills, and delay all dynamic features by 15 minutes. Some gaps remain. The original device exports are not available here, so completely prospective measurement provenance cannot be guaranteed. Meal logging delay is also imperfectly known. These limitations are material.

## Team details and college/incubator information

| Field | Details |
|---|---|
| Registered team | Team product |
| Leader / registered member | Dipanshu Raj |
| Institution | Indian Institute of Technology Kanpur |
| Programme | B.Tech., Materials Science and Engineering |
| GitHub account | Dipanshur19 |
| Project folder | `Team product_IIT Kanpur` |

No incubator affiliation is claimed. Team leader phone and email should be supplied in the submission form rather than copied into the public code repository. Development and documentation used AI assistance; the participant should review the code, results and video and be able to explain them to the jury.

## Open-source license details

Original application code: [MIT](LICENSE). Included CGMacros source data and processed data: **CC BY-NC-SA 4.0**, with attribution in [DATA_SOURCES.md](DATA_SOURCES.md). Trained model artifacts are distributed for noncommercial research under the same conservative share-alike terms; do not assume that the code's MIT license overrides data/model restrictions. Third-party software retains its own licenses.

## References

1. Gutierrez-Osuna et al. CGMacros v1.0.0. PhysioNet. https://doi.org/10.13026/3z8q-x658
2. Das et al. CGMacros: a pilot scientific dataset for personalized nutrition and diet monitoring. Scientific Data (2025). https://www.nature.com/articles/s41597-025-05851-7
3. Battelino et al. Clinical Targets for Continuous Glucose Monitoring Data Interpretation. Diabetes Care (2019). https://pubmed.ncbi.nlm.nih.gov/31177185/
4. scikit-learn histogram gradient boosting. https://scikit-learn.org/stable/modules/ensemble.html#histogram-based-gradient-boosting
