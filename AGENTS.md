# AGENTS.md

## LC Pipeline: AI Agent Guidance

### 1. Architecture Overview
- **Pipeline Structure:**
  - `main.py` orchestrates the ETL pipeline: load → clean → validate → report.
  - **Services:**
    - `services/data_cleaner.py`: Cleans raw data (unicode, whitespace, case normalization).
    - `services/validation_service.py`: Orchestrates all field and cross-field validators.
    - `services/report_service.py`: Generates output CSVs and summary reports.
  - **Validators:**
    - Located in `validators/`, each validator (e.g., `amount_validator.py`, `lei_validator.py`) implements a single responsibility, inheriting from `base.py`.
    - All validation rules and error codes are defined in `config/validation_rules.py` (no hardcoded logic in validators).
  - **Config:**
    - `config/constants.py`: Static values (currencies, regex, column names).
    - `config/settings.py`: Paths, filenames, API settings, pipeline options.
    - `config/validation_rules.py`: Centralized validation logic and error code registry.
  - **Models:**
    - `models/validation_error.py`: Standardized error object, string and dict representations.

### 2. Data Flow
- Input: `/data/input/lc_transactions_v3_shuffled.csv`
- Output: `/data/output/` (flagged_issues.csv, valid_transactions.csv, validation_report.csv, pipeline.log)
- Data is always processed as a pandas DataFrame.
- All intermediate and output files are written relative to project root (see `config/settings.py`).

### 3. Developer Workflows
- **Run full pipeline:**
  - `python main.py` (runs the entire ETL process, outputs logs and CSVs)
- **Test single validator:**
  - `pytest tests/test_amount_validator.py -v` (or any test in `tests/`)
- **Test full pipeline:**
  - See `test1/test_full_pipeline.py` for an end-to-end test script.
- **Jupyter analysis:**
  - Notebooks in `/notebooks/` and `/doc/notebooks/` demonstrate data exploration and merging outputs with lookup tables.

### 4. Project Conventions & Patterns
- **No hardcoded validation logic:** All rules and error codes are defined in `config/validation_rules.py` and imported by validators.
- **Composition over inheritance:** `ValidationService` and `ReportService` use (not inherit from) validators and error models.
- **Logging:**
  - Use `utils/logger.py`'s `get_logger()` for consistent logging to both console and `/data/output/pipeline.log`.
- **Path handling:**
  - All paths use `pathlib.Path` and are relative to the project root for portability.
- **Error codes:**
  - All error codes/messages/severity are centrally defined and accessible via `ALL_ERROR_CODES` in `config/validation_rules.py`.

### 5. Integration & Extension Points
- **GLEIF API:**
  - LEI validation uses GLEIF API (see settings in `config/settings.py`).
  - Caching and retries are configurable.
- **Adding new validation:**
  - Create a new validator in `validators/`, register it in `ValidationService`, and add rules/codes to `config/validation_rules.py`.
- **Output merging:**
  - Notebooks show how to join output CSVs with lookup tables (e.g., currency info, error codes) for analysis.

### 6. Key Files & Directories
- `main.py`, `services/`, `validators/`, `config/`, `models/`, `utils/`, `data/`, `tests/`, `notebooks/`
- See `/doc/` for markdown documentation of config, models, services, and validators.

---

For more, see https://agents.md/ and `/doc/` for detailed field-level and rule explanations.

