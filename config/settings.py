"""
═══════════════════════════════════════════════════════════════════════════════
Environment settings - paths, API configuration, pipeline options.

These values CAN change between development and production.
For static values that DON'T change, see constants.py
═══════════════════════════════════════════════════════════════════════════════
"""

from pathlib import Path

## PATHS
# _ ═══════════════════════════════════════════════════════════════════════════════
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"
OUTPUT_DIR = DATA_DIR / "output"

## FILE NAMES
# _═══════════════════════════════════════════════════════════════════════════════
INPUT_FILE = "lc_transactions_v3_shuffled.csv"

# Intermediate files (for learning - see each phase output!)
PHASE1_FILE = "phase1_loaded.csv"
PHASE2_FILE = "phase2_cleaned.csv"
PHASE3_FILE = "phase3_transformed"

# Final outputs
VALID_OUTPUT = "valid_transactions.csv"
FLAGGED_OUTPUT = "flagged_issues.csv"
REPORT_OUTPUT = "validation_report.csv"

## API SETTINGS (GLEIF.md)
# _ ═══════════════════════════════════════════════════════════════════════════════
GLEIF_API_BASE = "https://api.gleif.org/api/v1"  # Base URL for LEI validation API
GLEIF_TIMEOUT_SECONDS = 10  # Don't wait forever if API is slow
GLEIF_MAX_RETRIES = 3  # Try 3 times before giving up
GLEIF_CACHE_ENABLED = True  # Don't call API twice for same LEI!
GLEIF_CACHE_TTL_HOURS = 24  # Cache expires after 24 hours

## PIPELINE SETTINGS
# _ ═══════════════════════════════════════════════════════════════════════════════
SAVE_INTERMEDIATE_FILES = True  # save CSV after each phase (for learning!)
LOG_LEVEL = "DEBUG"  # DEBUG = everything, INFO = normal, ERROR = only problems
BATCH_SIZE = 50  # How many API calls before pause (respect rate limits)
