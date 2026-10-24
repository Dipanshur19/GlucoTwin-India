<![CDATA[<div align="center">

<!-- Title & Branding -->
# 🧬 GlucoTwin India

### An Adaptive Partial Digital Twin for Glucose Forecasting

[![Digital Twin Challenge 2026](https://img.shields.io/badge/🏆_Digital_Twin_Challenge-2026-gold?style=for-the-badge)](https://unstop.com)
[![Happiest Health](https://img.shields.io/badge/Happiest_Health-Partner-teal?style=for-the-badge)](https://happiestminds.com)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.8.0-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/Code-MIT-green?style=flat-square)](LICENSE)
[![Data: CC BY-NC-SA 4.0](https://img.shields.io/badge/Data-CC_BY--NC--SA_4.0-lightgrey?style=flat-square)](DATA_SOURCES.md)
[![Tests](https://img.shields.io/github/actions/workflow/status/Dipanshur19/GlucoTwin-India/checks.yml?style=flat-square&label=tests)](https://github.com/Dipanshur19/GlucoTwin-India/actions)

---

**Team product** · **Indian Institute of Technology Kanpur**
**Dipanshu Raj** · [GitHub @Dipanshur19](https://github.com/Dipanshur19)

</div>

---

> **GlucoTwin** fuses a participant's baseline clinical profile with real-time glucose sensor, wearable activity, and meal streams into a **patient-specific digital state** that evolves with every measurement. The prototype forecasts glucose at **30, 60, and 120 minutes**, provides **calibrated uncertainty intervals**, and generates **exploratory early-warning flags** for upcoming high-glucose episodes.

> [!WARNING]
> **Research prototype only.** These are retrospective results from a small US cohort (CGMacros). No Indian clinical validation, diagnosis, dosing, treatment benefit, regulatory approval, or live wearable integration is claimed.

---

## 📑 Table of Contents

| | Section | Description |
|---|---|---|
| 🎬 | [Demo Video](#-demo-video) | 20-minute prototype walkthrough on YouTube |
| 📊 | [Key Results](#-key-results--measured-outcomes) | Forecast accuracy, coverage & alert metrics |
| 🏥 | [Problem Statement](#-problem-statement--healthcare-use-case) | Healthcare context and task definition |
| 🚀 | [Quick Start](#-quick-start) | Get running in under 2 minutes |
| 🔬 | [How It Works](#-how-it-works--technical-stack) | Architecture, AI/ML pipeline & tech stack |
| 🗂️ | [Data Fusion](#-data-fusion--provenance) | Data sources, joins & preprocessing |
| 📁 | [Repository Map](#-repository-map) | Navigate every file in this submission |
| 👤 | [Team Details](#-team-details) | Team & institution information |
| 📜 | [License](#-license-details) | Open-source license breakdown |
| 📚 | [References](#-references) | Citations and data sources |

---

## 🎬 Demo Video

<div align="center">

<!-- VIDEO_LINK_START -->
[Watch the 20-minute prototype demonstration](https://youtu.be/Usu17YubcCw)
<!-- VIDEO_LINK_END -->

[![Watch Demo Video](https://img.shields.io/badge/▶_Watch_on_YouTube-20_min_Demo-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/Usu17YubcCw)

</div>

> The video covers participant selection, live sensor replay, forecast visualization with uncertainty bands, sensor outage handling, evidence comparison, scenario sandbox, and JSON export — all running locally with no API keys or GPU.

---

## 📊 Key Results & Measured Outcomes

<div align="center">

### 🎯 Forecast Accuracy — Patient-Macro MAE (mg/dL)

> Final test: **3 unseen T2D participants** · 24-hour warm-up excluded · Training: 36 participants · Validation: 3 · Calibration: 3

</div>

| Horizon | Persistence | Sensor-only | Fused | ✅ **Adaptive** | 📉 Improvement |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **30 min** | 19.74 | 21.22 | 20.34 | **18.48** | 🟢 **6.4% lower** |
| **60 min** | 26.67 | 29.26 | 26.88 | **24.12** | 🟢 **9.6% lower** |
| **120 min** | 35.26 | 35.86 | 33.41 | **29.00** | 🟢 **17.7% lower** |

<div align="center">

<img src="results/forecast.png" alt="Forecast MAE comparison across all horizons" width="700">

*Mean absolute error comparison — the Adaptive model (purple) consistently achieves the lowest error*

</div>

---

### 📈 Per-Patient Breakdown (60-min Horizon)

<div align="center">

<img src="results/patients.png" alt="Per-patient 60-minute MAE" width="700">

*The Adaptive model improves on every test patient individually*

</div>

---

### 🔔 Exploratory Alert Metrics

| Metric | Value |
|:---|:---:|
| Matched alerts / total alerts | **14 / 64** |
| Detected onsets / observable onsets | **14 / 66** |
| False alerts per eligible patient-day | **1.87** |
| Median lead time (matched alerts) | **15 min** |

<div align="center">

<img src="results/alerts.png" alt="Alert breakdown: matched vs false" width="600">

</div>

> [!CAUTION]
> These alert results are **exploratory** and not adequate for clinical deployment. A 60-minute forecast horizon must not be described as 60 minutes of demonstrated warning time.

---

### 🎯 Additional Metrics

| Metric | Value |
|:---|:---:|
| 90% interval coverage (60 min) | **89.8%** empirical |
| Training time (2 threads) | **26.8 seconds** |
| Model variant selected | **Adaptive** (all horizons) |
| Bootstrap 95% CI — 60 min MAE improvement | **1.70 – 3.15 mg/dL** |

---

## 🏥 Problem Statement & Healthcare Use Case

> Adults with **Type 2 diabetes** may experience glucose excursions between periodic clinical reviews. This proof-of-concept investigates whether paired baseline labs and continuous sensor history can support **patient-specific forecasting** and a **clinician review workflow**.

### Task Definition

| | Description |
|:---|:---|
| 🎯 **Primary task** | Forecast glucose **60 minutes** from current timestamp |
| 📐 **Secondary horizons** | 30 minutes and 120 minutes |
| ⏱️ **Input delay** | Sensor stream deliberately delayed by **15 minutes** |
| 🚨 **Event endpoint** | New crossing above **180 mg/dL** followed by 3 consecutive 5-min bins > 180, all within 60 minutes |

> [!NOTE]
> The 180 mg/dL threshold is a **study endpoint**, not an emergency threshold or patient-specific treatment target.

---

## 🚀 Quick Start

> **Requirements:** Python 3.12 · No GPU, API key, or paid service needed · First run needs internet for pip

### Option A — One-click

| Platform | Command |
|:---|:---|
| 🪟 **Windows** | Double-click `start_windows.bat` |
| 🍎 **macOS / 🐧 Linux** | `bash start.sh` |

### Option B — Terminal

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
python -m pip install -r requirements.txt

# 4. Launch the dashboard
python app.py
```

> Open **http://127.0.0.1:8765** if the browser doesn't launch automatically.
> After initial setup, everything works **fully offline**.

---

### 🖥️ Prototype Walkthrough

```
1️⃣  Select a held-out study participant → inspect clinical profile
2️⃣  Step forward or play historical sensor replay
3️⃣  Review 3 forecast horizons, 90% intervals & ranking score
4️⃣  Toggle "Reveal observed future" for retrospective inspection
5️⃣  Simulate a sensor outage → all forecasts withheld
6️⃣  Open "Evidence" → compare baselines & alert limitations
7️⃣  Open "Scenario sandbox" → synthetic response illustration
8️⃣  Export a JSON review record (no data transmitted)
```

---

## 🔬 How It Works — Technical Stack

### Technology Stack

| Component | Technology |
|:---|:---|
| **Language** | Python 3.12 |
| **Core ML** | scikit-learn 1.8.0 (Histogram Gradient Boosting) |
| **Numerical** | NumPy 2.3.5 · pandas 2.2.3 · SciPy 1.17.0 |
| **Serialization** | joblib 1.5.3 |
| **Frontend** | Dependency-free HTML/CSS/JavaScript with Canvas charts |
| **Server** | Python standard library (localhost only) |

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      GlucoTwin Pipeline                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐    ┌──────────────┐    ┌──────────────────┐     │
│   │ Baseline │    │  CGM Sensor  │    │   Meal Logging   │     │
│   │  Labs &  │───▶│  Stream      │───▶│   Stream         │     │
│   │ Profile  │    │  (15m delay) │    │  (decay states)  │     │
│   └──────────┘    └──────┬───────┘    └────────┬─────────┘     │
│                          │                      │               │
│                    ┌─────▼──────────────────────▼─────┐        │
│                    │    Feature Engineering Layer      │        │
│                    │  • Rolling glucose summaries      │        │
│                    │  • Activity integration           │        │
│                    │  • Decaying meal states            │        │
│                    │  • Clinical context features       │        │
│                    └─────────────┬────────────────────┘        │
│                                 │                               │
│              ┌──────────────────┼──────────────────┐           │
│              ▼                  ▼                   ▼           │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │  30-min GBR  │  │  60-min GBR  │  │ 120-min GBR  │        │
│   │  Regressor   │  │  Regressor   │  │  Regressor   │        │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│          │                  │                  │                │
│   ┌──────▼──────────────────▼──────────────────▼───────┐       │
│   │     Adaptive Residual Correction (per-patient)     │       │
│   │  Bounded EWMA of observable errors per horizon     │       │
│   └──────────────────────┬─────────────────────────────┘       │
│                          │                                      │
│          ┌───────────────┼───────────────┐                     │
│          ▼               ▼               ▼                     │
│   ┌────────────┐  ┌────────────┐  ┌──────────────┐            │
│   │ Forecasts  │  │   90% CI   │  │  Alert Score │            │
│   │  (mg/dL)   │  │ (calibr.)  │  │  (GBC rank)  │            │
│   └────────────┘  └────────────┘  └──────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Model Details

> **Three histogram gradient-boosting regressors** predict glucose changes at each horizon, using clinical context and causal sensor/meal features. A **bounded exponentially weighted residual correction** personalizes each horizon using only errors whose outcomes are already observable. A separate **gradient-boosting classifier** ranks episode risk.

> [!IMPORTANT]
> The classifier's class-weighted score is a **ranking score**, not a calibrated probability.

| Stage | Method |
|:---|:---|
| Model selection | Validation patients choose between fused & adaptive variants |
| Interval calibration | Separate calibration patients determine empirical 90% residual intervals |
| Final evaluation | Test patients use **no** model/threshold/interval selection |
| Deployed variant | **Adaptive** at all three horizons |

📄 **Full details:** [Architecture PDF](docs/GlucoTwin_Architecture.pdf) · [Technical Report](docs/GlucoTwin_Technical_Report.pdf) · [Model Card](MODEL_CARD.md)

---

## 🗂️ Data Fusion & Provenance

**[CGMacros v1.0.0](https://doi.org/10.13026/3z8q-x658)** · 45 participants · 14 T2D

| Aspect | Details |
|:---|:---|
| **Join key** | Same participant ID across demographics/labs and sensor records |
| **Clinical profile** | EHR-like baseline representation (no real hospital EHR connection) |
| **Sensor cadence** | Integer Dexcom readings; no added interpolation or backward fills |
| **Feature delay** | All dynamic features delayed by **15 minutes** |
| **Data integrity** | No unrelated Synthea records attached to real sensor traces |

> [!NOTE]
> The original device exports are not available, so fully prospective measurement provenance cannot be guaranteed. Meal logging delay is imperfectly known. These limitations are material.

📄 **Full details:** [Data Sources & Licenses](DATA_SOURCES.md) · [Reproducibility Guide](REPRODUCIBILITY.md)

---

## 📁 Repository Map

```
Team product_IIT Kanpur/
│
├── 📄 README.md                          ← You are here
├── 📄 LICENSE                            ← MIT (code)
├── 📄 MODEL_CARD.md                      ← Model documentation
├── 📄 DATA_SOURCES.md                    ← Data provenance & licenses
├── 📄 REPRODUCIBILITY.md                 ← Reproduction instructions
├── 📄 SUBMISSION_CHECKLIST.md            ← Submission verification
│
├── 🐍 app.py                            ← Dashboard server (localhost:8765)
├── 📋 requirements.txt                   ← Python dependencies
├── 🪟 start_windows.bat                  ← Windows quick-start
├── 🐧 start.sh                           ← macOS/Linux quick-start
│
├── 📦 glucotwin/                         ← Core Python package
│   ├── __init__.py
│   ├── core.py                           ← Inference engine
│   ├── prepare.py                        ← Data preparation
│   ├── service.py                        ← HTTP API service
│   └── train.py                          ← Model training pipeline
│
├── 🗄️ data/                              ← Processed data & EHR profiles
│   ├── source_csv.zip                    ← Original CGMacros CSVs
│   ├── ehr/                              ← Per-patient clinical profiles
│   └── patient_*.csv.gz                  ← Prepared sensor/meal streams
│
├── 🤖 models/
│   ├── glucotwin.joblib                  ← Trained model artifact
│   └── LICENSE.md                        ← CC BY-NC-SA 4.0 (model)
│
├── 📊 results/                           ← Evaluation outputs
│   ├── summary.json                      ← Full metrics summary
│   ├── forecast_metrics.csv              ← Horizon-level metrics
│   ├── per_patient_metrics.csv           ← Per-patient breakdown
│   ├── forecast.png                      ← MAE comparison chart
│   ├── patients.png                      ← Per-patient chart
│   └── alerts.png                        ← Alert breakdown chart
│
├── 📑 docs/                              ← Submission documents
│   ├── GlucoTwin_Presentation.pdf        ← Presentation deck
│   ├── GlucoTwin_Presentation.pptx       ← Editable PowerPoint
│   ├── GlucoTwin_Architecture.pdf        ← Architecture diagram
│   ├── GlucoTwin_Technical_Report.pdf    ← Technical report
│   ├── Demo_Script.md                    ← Video script
│   ├── Demo_Captions.srt                 ← Video captions
│   ├── Jury_QA.md                        ← Jury Q&A preparation
│   └── Submission_Guide.pdf              ← Submission checklist
│
├── 🧪 tests/
│   └── test_core.py                      ← 12 reproducibility tests
│
├── 🌐 web/
│   └── index.html                        ← Dashboard frontend
│
├── 🔧 scripts/
│   ├── finalize_submission.py            ← Insert video/repo URLs
│   └── check_submission.py               ← Verify package completeness
│
└── ⚙️ .github/workflows/
    └── checks.yml                        ← CI: tests on push/PR
```

---

## 👤 Team Details

<div align="center">

| | Field | Details |
|:---:|:---|:---|
| 👥 | **Registered team** | Team product |
| 👨‍💻 | **Team leader** | **Dipanshu Raj** |
| 🏫 | **Institution** | **Indian Institute of Technology Kanpur** |
| 📚 | **Programme** | B.Tech., Materials Science and Engineering |
| 🐙 | **GitHub** | [@Dipanshur19](https://github.com/Dipanshur19) |
| 📁 | **Project folder** | `Team product_IIT Kanpur` |
| 🏢 | **Incubator** | None claimed |

</div>

> [!NOTE]
> Team leader contact details are supplied via the submission form and not published in the repository. Development and documentation used AI assistance; the participant should review the code, results, and video and be able to explain them to the jury.

---

## 📜 License Details

| Component | License | Notes |
|:---|:---|:---|
| Application code | [![MIT](https://img.shields.io/badge/MIT-green?style=flat-square)](LICENSE) | Full open source |
| CGMacros data | [![CC BY-NC-SA 4.0](https://img.shields.io/badge/CC_BY--NC--SA_4.0-lightgrey?style=flat-square)](DATA_SOURCES.md) | Noncommercial, share-alike |
| Trained model | **CC BY-NC-SA 4.0** | Follows data license restrictions |
| Third-party libs | Various | Retain their own licenses |

> [!IMPORTANT]
> Do not assume the code's MIT license overrides data/model restrictions. See [DATA_SOURCES.md](DATA_SOURCES.md) for full attribution.

---

## 📚 References

1. Gutierrez-Osuna et al. **CGMacros v1.0.0.** PhysioNet. [doi:10.13026/3z8q-x658](https://doi.org/10.13026/3z8q-x658)
2. Das et al. **CGMacros: a pilot scientific dataset for personalized nutrition and diet monitoring.** *Scientific Data* (2025). [Nature](https://www.nature.com/articles/s41597-025-05851-7)
3. Battelino et al. **Clinical Targets for Continuous Glucose Monitoring Data Interpretation.** *Diabetes Care* (2019). [PubMed](https://pubmed.ncbi.nlm.nih.gov/31177185/)
4. **scikit-learn histogram gradient boosting.** [Documentation](https://scikit-learn.org/stable/modules/ensemble.html#histogram-based-gradient-boosting)

---

<div align="center">

**Built with 💡 at IIT Kanpur for the Digital Twin Challenge 2026**

[![GitHub](https://img.shields.io/badge/View_on-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/Dipanshur19/GlucoTwin-India)
[![YouTube](https://img.shields.io/badge/Watch_Demo-YouTube-FF0000?style=for-the-badge&logo=youtube)](https://youtu.be/Usu17YubcCw)

</div>
]]>
