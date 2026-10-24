# Jury questions and defensible answers

**Why call this a Digital Twin?** It maintains a patient-linked evolving state, synchronizes as new sensor observations arrive, and produces individualized forecasts. The residual state learns from matured errors. It is a partial data-driven twin, not a validated physiological replica.

**Where is the EHR?** We transform baseline demographics and laboratory values from the same participant into a structured EHR-like record. A hospital integration is not implemented. Both streams share the source participant identifier.

**What is new?** The demonstrable contribution is an auditable package combining paired clinical/sensor data, horizon-aware delayed adaptation, uncertainty reporting, missing-data suppression and a transparent evaluation dashboard. We do not claim the first diabetes twin or a new foundational algorithm.

**Does the model really predict two hours ahead?** It produces a glucose estimate at a two-hour horizon and we report its error. That is not the same as reliably predicting an adverse event two hours before onset. The alert experiment's median matched warning is fifteen minutes.

**Did fusion itself improve everything?** No. The fused model alone does not beat persistence at every horizon. The strongest results include residual adaptation. All ablations are published.

**Are the alerts ready for doctors to rely on?** No. Precision and recall are low in the small held-out test. They are an exploratory review flag within a research demo, not an autonomous clinical alarm.

**Why not an LSTM or a transformer?** There are only fourteen T2D participants. A compact boosted model is fast, reproducible and supports missing values. Model complexity is not evidence of better generalization. More data and preregistered comparisons are needed before increasing complexity.

**How is leakage controlled?** Participant-disjoint partitions, causal feature construction, delayed feedback, no added backward interpolation and prefix-invariance tests. The source's upstream interpolation remains a limitation because native device exports are not available.

**What can a scenario slider tell us?** Only what the explicitly assumed mathematical response would look like. It does not establish a causal effect of food or exercise and cannot guide treatment.

**Why India if the dataset is American?** India is the intended workflow context, not the validated population. The next step is clinician-supervised evaluation on representative Indian data, including local diet and care patterns. We make no Indian accuracy or affordability claim.

**What about privacy and regulation?** This package uses open anonymized study data. It collects no new patient data. A real deployment would require appropriate governance, consent, security, clinical evaluation and regulatory assessment; none is certified by this prototype.

**How would you improve it next?** Obtain native CGM data, expand T2D cohorts, resolve meal logging latency, improve and calibrate event risk, validate across sensors and subgroups, and run a prospective silent study before exposing clinicians to alerts.
