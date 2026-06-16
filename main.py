from logging import info

import pandas as pd
from config import settings
from services.data_cleaner import DataCleaner
from services.validation_service import ValidationService
from services.report_service import ReportService
from utils.decorators import timer
from utils.logger import get_logger

logger = get_logger('pipeline')

@timer
def load_data():
    file_path = settings.INPUT_DIR / settings.INPUT_FILE
    df = pd.read_csv(file_path)
    logger.info(f"Loaded: {len(df)} transactions")
    return df


@timer
def clean_data(df):
    cleaner = DataCleaner()
    cleaned = cleaner.clean(df)
    logger.info(f"Cleaned: {len(cleaned)} transactions")
    return cleaned


@timer
def validate_data(df):
    validator = ValidationService()
    return validator.validate_all(df)


@timer
def generate_reports(df, results):
    reporter = ReportService(df, results)
    reporter.save_reports()


def main() -> None:
    """Run the full LC validation pipeline."""
    logger.info("\n=== LC VALIDATION PIPELINE ===\n")

    df = load_data()
    cleaned = clean_data(df)
    results = validate_data(cleaned)
    generate_reports(cleaned, results)

    # Summary
    total_errors = sum(len(errs) for errs in results.values())
    flagged = sum(1 for errs in results.values() if errs)
    clean = sum(1 for errs in results.values() if not errs)

    logger.info(f"\n=== PIPELINE COMPLETE ===")
    logger.info(f"Clean: {clean} | Flagged: {flagged} | Errors: {total_errors}")


if __name__ == '__main__':
    main()

    # cat data/output/pipeline.log _.  check your log file