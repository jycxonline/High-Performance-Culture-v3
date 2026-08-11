# High Performance Diagnostic Tool — v3.4 (PACE)

**Powered by Cathay Academy.** Framework = **PACE**: **P**urpose · **A**lliance · **C**oordination · **E**xcellence.

## What changed in v3.4

1. **Element renamed:** *Collaboration* → **Coordination** everywhere (questionnaire, analysis,
   charts, PDF, action library, checkpoints). The **PACE** acronym still holds (P-A-C-E).
   Legacy support: any old data or config that still says "Collaboration" is automatically
   mapped to "Coordination" on load, so existing uploads keep working.
2. **British English spelling** applied across all questions and diagnostic text, e.g.:
   - organization → **organisation** (Q02, Q06)
   - behaviors → **behaviours** (Q11)
   - characterized → **characterised** (Q13)
   - modeled → **modelled** (Q33)
   - recognize → **recognise** (Q39)
   - prioritise, rationalise, standardising, analyse, colour, centre — all British forms.

## Run locally

```bash
unzip HPC_Diagnostic_Tool_v3.4.zip
cd hpc_tool
./run.sh              # macOS / Linux  (or run.bat on Windows)
```
Opens at `http://localhost:8501`. First run installs dependencies (~1 min).

## Deploy to Streamlit Cloud

Copy the contents of `hpc_tool/` into the root of your GitHub repo (overwriting `app.py`, `hpc/`,
`data/`), commit & push, then reboot the app. Confirm the footer reads **v3.4**.

## Version

- Tool: 3.4.0 · Framework: PACE (Purpose · Alliance · Coordination · Excellence)
- Spelling: British English
- 34 departments · broad health spectrum · Powered by Cathay Academy
