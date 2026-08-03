# High Performance Diagnostic Tool — v3 (PACE)

**Powered by Cathay Academy.** Framework = **PACE**: Purpose · Alliance · Collaboration · Excellence.

## What was fixed in v3 (from your feedback)

1. **Admin Dashboard crash (`Department not in data`)** — fixed. The dashboard now
   analyses against the full dataset, and `analyze()` falls back to company-wide instead
   of raising if a focus department is ever missing.
2. **Report not clear / focus name too big** — the giant title is gone; the focus is a
   compact one-line header. No cramped combined image.
3. **One-page combined report removed on screen** — replaced with clear, individual
   charts at readable sizes.
4. **Radar was a solid block** — now an outline style: navy solid line + gold dashed
   company line, with value labels, so both series are clearly comparable.
5. **Company-wide chart too small** — all charts enlarged and laid out 2-per-row.
6. **Polarisation analysis repeated the same closing sentence** — each element now has a
   distinct, element-specific closing recommendation.
7. **Tables scrolled sideways** — Tailored Recommendations and Polarisation are now
   cards (2-column, wrap, no horizontal scroll); rule-based insights are bullets.
8. **PACE runner label** — now shows the **department** (name in header + on the runner).

## Quick start

```bash
unzip HPC_Diagnostic_Tool_v3.zip
cd hpc_tool
./run.sh              # macOS / Linux  (or run.bat on Windows)
```
Opens at `http://localhost:8501`. First run installs dependencies (~1 min).

## Try it

| Page | Try | You'll see |
|---|---|---|
| 📊 Admin Dashboard | Focus = **Information Technology** | Clear charts + polarised Alliance/Collaboration written analysis (distinct endings) + tailored recommendation cards |
| 📊 Admin Dashboard | Focus = **Company-wide** | Larger, readable charts (no crash) |
| 🏃 PACE | **PC — People & Culture** | Runner mid-journey, labelled with the department |
| 🏃 PACE | **CA — Cathay Academy** | Runner at the Finish Line |

## Pages

**Diagnostic** — Home · Take Questionnaire *(no defaults; all 40 required)* ·
Admin Dashboard *(single combined view)* · Generate Executive Report *(one-page PDF)* ·
Upload Response Data · Upload Configuration

**PACE** — PACE *(running-track journey)* · Submit Action Plan · Checkpoint Update · PACE Admin

## Version

- Tool: 3.0.0 · Framework: PACE
- Schema (config): HPC-CONFIG-v2 · Schema (lookup): PACE-DEPTLOOKUP-v1
- Powered by Cathay Academy
