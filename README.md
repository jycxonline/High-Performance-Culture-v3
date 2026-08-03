# High Performance Diagnostic Tool — v3.1 (PACE)

**Powered by Cathay Academy.** Framework = **PACE**: Purpose · Alliance · Collaboration · Excellence.

## What changed in v3.1 (from your feedback)

1. **Dashboard `AttributeError` at `polarisation_bar` fixed** — the chart is rebuilt with plain
   floats, ASCII legend labels and `getattr` guards, and **every chart on the dashboard is now
   wrapped** so a single chart can never crash the page.
2. **Department list updated to the 34 departments** from your Excel (APD → EXO). They flow through
   the config, the sample response data (so every department has data), and the PACE lookup.
3. **More professional visuals** — cleaner palette, consistent titles/gridlines, a tidy focus strip
   instead of oversized metric text, recommendation & polarisation **cards** (no sideways scrolling),
   and the full 34-department ranking moved into an expander so the main view stays clean.
4. The config loader now tolerates either **"Department Name"** or **"Department Names"** headers, so
   your exact Excel uploads cleanly.

## Quick start

```bash
unzip HPC_Diagnostic_Tool_v3.1.zip
cd hpc_tool
./run.sh              # macOS / Linux  (or run.bat on Windows)
```
Opens at `http://localhost:8501`. First run installs dependencies (~1 min).

## Try it

| Page | Try | You'll see |
|---|---|---|
| 📊 Admin Dashboard | Focus = **IMT - Information Technology** | Clear charts + polarised Alliance/Collaboration analysis + tailored recommendation cards |
| 📊 Admin Dashboard | Focus = **Company-wide** | Larger readable charts across all 34 departments (no crash) |
| 🏃 PACE | Any department | Runner on the straight PACE track, labelled with the department |

## Deploying to Streamlit Cloud (`high-performance-culture-v3`)

Replace the repo contents with this package and redeploy. The `polarisation_bar` crash and the
department-not-found error are both resolved, and the 34 departments are loaded.

## Version

- Tool: 3.1.0 · Framework: PACE · 34 departments
- Schema (config): HPC-CONFIG-v2 (accepts "Department Name" / "Department Names")
- Schema (lookup): PACE-DEPTLOOKUP-v1
- Powered by Cathay Academy
