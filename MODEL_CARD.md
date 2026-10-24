# GlucoTwin model card — version 1.0.0

**Owner:** Dipanshu Raj, Team product, IIT Kanpur. **Date:** 23 October 2026.

## Intended use
Research demonstration of a partial data-driven Digital Twin for adult Type 2 diabetes glucose forecasting and retrospective clinician-dashboard exploration. Not for patient treatment, medication changes, insulin dosing, diagnosis, emergency response or unsupervised clinical alerts. No pediatric, pregnancy or Type 1 diabetes claim.

## Inputs and outputs
Static: age, recorded sex indicator, BMI, HbA1c and fasting glucose. Dynamic: glucose history, activity METs, heart rate and recorded meal macronutrients. Evolving state: lagged/rolling glucose, decaying meal loads and horizon-specific residual memory. Outputs: glucose point forecasts at 30/60/120 min, empirical residual intervals, an uncalibrated episode ranking score, and a quality gate.

## Model construction
Histogram gradient boosting predicts a change from the latest available glucose. Six regressors support sensor-only and fused comparisons. The adaptive variant adds a bounded exponentially weighted residual correction with fixed gain 0.35. Residuals are updated only when the corresponding target is observable after the 15-minute input delay. A separate class-balanced histogram gradient-boosting classifier ranks new episode risk. Its score is not a probability.

## Evaluation
Patient-disjoint seed 2026. Training IDs: [1, 2, 4, 6, 7, 8, 9, 10, 11, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 41, 42, 43, 44, 45, 48, 49]. Validation IDs: [12, 46, 14]. Calibration IDs: [39, 47, 3]. Test IDs: [35, 5, 38]. Exclude the first 24 hours from scoring. Models, selected variants and alert thresholds are fixed before final test evaluation. Only earlier measurements can update test-patient state.

| Horizon | Persistence MAE | Sensor-only MAE | Fused MAE | Adaptive MAE | Adaptive vs persistence |
|---|---:|---:|---:|---:|---:|
| 30 min | 19.74 | 21.22 | 20.34 | 18.48 | 6.4% lower |
| 60 min | 26.67 | 29.26 | 26.88 | 24.12 | 9.6% lower |
| 120 min | 35.26 | 35.86 | 33.41 | 29.00 | 17.7% lower |

The fused model alone does not beat persistence at every horizon. Adaptive residual memory provides the strongest test result here. This prevents attributing every improvement to clinical-feature fusion alone.

Alert precision 21.9%, recall 21.2%, false alerts 1.87/eligible patient-day. Median matched warning 15 min. Alerts are exploratory and not clinically deployable.

## Uncertainty
Absolute residual radii are estimated on calibration patients. Coverage is reported as a patient-macro average. Windows overlap and patients share temporal dependence, so no distribution-free guarantee is asserted. Patient bootstrap confidence intervals use just three test patients and are highly unstable; see summary.json. They are descriptive, not evidence of population-level efficacy.

## Quality gate
Suppress forecasts when sensor age exceeds 20 min, the latest reading is missing, fewer than 18 of the last 24 glucose bins are present, or less than 24 h of history is available. The GUI outage toggle tests suppression. The service exposes only bundled test participants; it is not a general clinical upload or EHR integration service.

## Principal limitations
Small T2D cohort (14); only three final test participants; US rather than Indian data; observed meal inputs may have logging latency; upstream interpolation; no drug, adherence, renal function or sleep features; no intervention causality; one fixed random split; no prospective or clinical expert validation; uncalibrated classifier scores; broad prediction intervals; imperfect alarm precision and sensitivity. No regulatory, DPDP or HIPAA compliance certification is claimed.

## Monitoring required before future clinical work
Obtain native CGM exports and clinician oversight; preregister targets and evaluation; validate on larger representative Indian cohorts; calibrate risk probabilities; assess sensor and demographic subgroups; characterize alert burden; conduct a prospective silent evaluation. Treatment recommendations remain outside scope.
