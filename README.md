# High Performance Diagnostic Tool — v2 (PACE)

**Powered by Cathay Academy.** The framework is now **PACE**:

| PACE | Element |
|------|---------|
| **P** | Purpose |
| **A** | Alliance *(was Partnership)* |
| **C** | Collaboration *(was Processes)* |
| **E** | Excellence |

## What's new in v2

1. **Framework renamed** to PACE across the questionnaire, analysis, charts and report.
2. **Questionnaire has no default scores** — every question starts blank and **all 40 must be answered** before the form can be submitted (a live counter + warning enforces this).
3. **"Powered by the PERILL framework" removed everywhere**, replaced with **"High Performance Diagnostic Tool - Powered by Cathay Academy"**.
4. **Admin Dashboard = one combined view**:
   - A single **one-page compact report** (radar, element means, polarisation profile, ranking, correlation — all shrunk to fit one screen / one PDF page).
   - **Polarisation & Variance Analysis** — written statements per element (mean, SD, % low/mid/high, and whether views are polarised).
   - **Tailored actionable recommendations** — data-driven, keyed to each element's score *and* its polarisation pattern.
5. **"Flight Path Journey" renamed to "PACE"** with a **straight-line running-track** roadmap.
6. **New PACE stages** (straight line): Warm-up Exercise → Training → Reflect → Implement Change → Reflect → Training - Tempo → Race 'up your PACE' → Finish Line.

## Quick start

```bash
unzip HPC_Diagnostic_Tool_v2.zip
cd hpc_tool
./run.sh              # macOS / Linux  (or double-click run.bat on Windows)
```
Opens at `http://localhost:8501`. First run installs dependencies (~1 min).

## See it immediately

| Page | Try | You'll see |
|---|---|---|
| 📊 Admin Dashboard | Focus = **Information Technology** | One-page report + polarised **Collaboration/Alliance** written analysis + tailored recs |
| 🏃 PACE | **PC — People & Culture** | Runner mid-journey on the straight PACE track |
| 🏃 PACE | **CA — Cathay Academy** | Runner at the Finish Line |

## 10 pages

**Diagnostic** — Home · Take Questionnaire *(no defaults, all required)* · Admin Dashboard *(single insights view)* ·
Generate Executive Report *(one-page PDF)* · Upload Response Data · Upload Configuration

**PACE** — PACE *(running-track journey)* · Submit Action Plan · Checkpoint Update · PACE Admin

## Project layout

```
hpc_tool/
├── app.py                              # Streamlit router (branding + no-default questionnaire)
├── requirements.txt · run.sh · run.bat · README.md
├── build_all_data.py                   # rebuilds all Excel data (PACE)
├── hpc/
│   ├── config_loader.py                # PILLARS = Purpose, Alliance, Collaboration, Excellence
│   ├── engine.py                       # scoring + Polarisation & Variance + tailored recs
│   ├── charts.py                       # compact charts + one_page_dashboard()
│   ├── report.py                       # one-page landscape PDF
│   └── gamification/
│       ├── engine.py                   # PACE running stages
│       ├── pace_track.py               # straight-line running-track visual
│       └── pages.py                    # PACE Streamlit pages
└── data/
    ├── HPC_Question_Bank_Template.xlsx   # 40 Q (PACE) + 8 depts + config
    ├── HPC_Response_Data_Template.xlsx   # 144 sample respondents (with polarised elements)
    ├── PACE_Department_Lookup.xlsx       # PACE journey lookup (runner columns)
    └── action_plans/ · generated/
```

## Version

- Tool: 2.0.0 · Framework: PACE
- Schema (config): HPC-CONFIG-v2 · Schema (lookup): PACE-DEPTLOOKUP-v1
- Powered by Cathay Academy
