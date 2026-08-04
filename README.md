# High Performance Diagnostic Tool — v3.3 (PACE)

**Powered by Cathay Academy.** Framework = **PACE**: Purpose · Alliance · Collaboration · Excellence.

---

## ⚠️ IMPORTANT — why your app still crashed

The traceback you saw pointed to **`/mount/src/high-performance-culture-v3/app.py` line 255**
calling `charts.polarisation_bar(analysis.polarisation)`. That is the **OLD code** — the previous
fix had not yet been pushed to the deployed GitHub repo, so Streamlit Cloud was still running it.

v3.3 makes this crash **impossible in three independent ways**:

1. The fragile stacked `polarisation_bar` is **replaced** by a robust `variance_chart`
   (mean ± 1 SD whiskers, only basic matplotlib) **and** a **native Streamlit distribution
   table** that uses no matplotlib at all.
2. **Backwards-compatibility shims** are kept, so even if some old code still calls
   `charts.polarisation_bar(analysis.polarisation)`, it now routes to the robust chart and
   `analysis.polarisation` still returns the data — **no AttributeError**.
3. The **entire dashboard body is wrapped in try/except**, so nothing can white-screen the app.

## ✅ How to actually fix the deployment (do this)

Your Streamlit app deploys from the GitHub repo `high-performance-culture-v3`.
You must push these files to that repo, then reboot the app:

1. Unzip this package.
2. Copy **all** contents of `hpc_tool/` into the root of your GitHub repo,
   **overwriting** `app.py`, the `hpc/` folder, and the `data/` folder.
3. Commit & push to the branch Streamlit deploys from (usually `main`).
4. In Streamlit Cloud → your app → **⋮ → Reboot** (or it auto-redeploys on push).
5. Confirm the footer reads **v3.3** — that tells you the new code is live.

> Tip: In Streamlit Cloud, click **“Manage app” → Logs** and check the top line shows the new
> commit hash after pushing. If it still shows the old commit, the push didn't reach the deployed branch.

## Broader spectrum (some departments now dysfunctional)

Sample data now spans the full health range:

- **At Risk (dysfunctional):** ASD, PSD, OPN, IOC (scores ~2.9–3.2)
- **Developing:** CCD, DEX, DGT, CED, ISD, PVO, SUB
- **Performing:** most corporate/commercial teams
- **High Performance:** CAY, FIN, GIA, GLC, EXO, SND (scores ~7.7–8.2)
- **Split view (polarised):** IMT (Collaboration + Alliance), ENG (Alliance)

## Run locally

```bash
unzip HPC_Diagnostic_Tool_v3.3.zip
cd hpc_tool
./run.sh              # macOS / Linux  (or run.bat on Windows)
```

## Version

- Tool: 3.3.0 · Framework: PACE · 34 departments · broad health spectrum
- `polarisation_bar` retained only as a safe alias → `variance_chart`
- `analysis.polarisation` retained as a safe alias → `analysis.distribution`
- Powered by Cathay Academy
