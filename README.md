# LC Pipeline — MT700 SWIFT Letter of Credit Validation

A Python pipeline that validates **Letter of Credit (LC) / MT700 SWIFT messages**
against eight rule sets, flags anomalies, assigns severity, and surfaces the
results in an interactive Streamlit dashboard.

## Live Demo

**[Open the dashboard](https://norellaj26-lc-pipeline-streamlit-apps05-dashboard-glbmft.streamlit.app/)**

> Deployed on Streamlit Community Cloud. First load may take a few seconds if the
> app has gone to sleep — that's normal for the free tier.

## What this is

Trade-finance banks receive Letters of Credit as SWIFT MT700 messages. Before a
bank acts on one, the LC has to be checked: are the dates coherent, the amounts
valid, the parties identifiable (LEI), the banks real (BIC/SWIFT), the shipment
terms consistent? This pipeline automates that check across a dataset of 200
LCs and produces a forensic breakdown of what's wrong and how urgent it is.

| Metric           | Value                     |
|------------------|---------------------------|
| Total LCs        | 200                       |
| Clean            | 72                        |
| Flagged          | 128 (64%)                 |
| Total errors     | 237 across 8 validators   |
| Top error source | LEI validator (92 errors) |

## Tech

Python, pandas, matplotlib, Streamlit. Architecture leans on dataclasses, enums,
abstract base classes, and full type hints. Every validator inherits from a
common BaseValidator (ABC); errors are typed objects, never bare strings.

---

## How to run it (Future-Norella, read this part)

### Run the dashboard locally

From the repo root (~/projects/lc_pipeline):

    streamlit run streamlit_apps/05_dashboard.py

Must be run from the repo root — the entrypoint lives in a subfolder but adds the
project root to sys.path itself, so imports and the CSV path resolve.

### Re-run the validation pipeline

To regenerate data/output/validation_report.csv:

    python main.py

Loads the input CSV, cleans it, runs all 8 validators, writes the report. The
dashboard reads that report — it does NOT run the pipeline.

### Push an update (this auto-deploys!)

    git add -A
    git commit -m "your message"
    git push

WARNING: Every push to main auto-redeploys the live app within ~1 minute.
Run git diff before committing — what you push goes public.

---

## Gotchas (the scars — earned the hard way, do not relearn)

| Symptom                                  | Cause / Fix                                                                 |
|------------------------------------------|------------------------------------------------------------------------------|
| venv/ keeps reappearing in git add       | The .gitignore did not actually exist. Verify: ls -la .gitignore and git check-ignore -v venv/. A .gitignore you cannot cat does not exist. |
| __pycache__ / .pyc got committed         | Same cause. Added before the ignore rule existed. git rm --cached un-tracks without deleting. |
| Severity filter behaves oddly            | The severity column uses the string 'NONE' for clean LCs — NOT NaN.          |
| Charts look blurry / upscaled            | Use st.image(figure_to_png_bytes(fig), width=N), NOT st.pyplot(). st.pyplot upscales on high-DPI monitors. |
| Deploy fails with ModuleNotFoundError    | Streamlit Cloud runs from repo root. The sys.path.insert in the dashboard handles the subfolder entrypoint — keep it. |
| Build slow / installs Jupyter            | requirements.txt is deploy-lean (streamlit, pandas, matplotlib only). Never pip freeze the whole venv. |
| Real credentials                         | Live in .streamlit/secrets.toml, which is gitignored. Never commit a real secret or real SWIFT data. |

---

## Project structure

    lc_pipeline/
    |- config/            # constants, settings, validation_rules
    |- models/            # validation_error (typed error objects)
    |- validators/        # 8 validators, all inherit BaseValidator (ABC)
    |  |- api/            # gleif_client (LEI lookups)
    |- services/          # data_cleaner, validation_service,
    |                     # report_service, dashboard_charts
    |- utils/             # logger, decorators
    |- streamlit_apps/    # 05_dashboard.py = production dashboard
    |- data/output/       # validation_report.csv (dashboard data source)
    |- notebooks/         # exploration + visualization
    |- tests/             # validator unit tests
    |- main.py            # pipeline orchestration (no business logic)
    |- requirements.txt   # deploy-lean: streamlit, pandas, matplotlib

## The 8 validators

| Code | Validator | Checks                                     |
|------|-----------|--------------------------------------------|
| LEI  | LEI       | Legal Entity Identifier format + GLEIF     |
| SHIP | Shipment  | Shipment dates, ports, transhipment terms  |
| AMT  | Amount    | Amount validity, currency, tolerance       |
| XVAL | Cross     | Cross-field consistency (dates vs dates)   |
| DATE | Date      | Issue / expiry / latest-shipment coherence |
| LC   | LC        | LC number + form (MT700) structure         |
| BIC  | SWIFT     | Bank BIC/SWIFT code validity               |
| PTY  | Party     | Applicant / beneficiary completeness       |
