import pandas as pd
from typing import List, Dict
from models.validation_error import ValidationError
from config import settings
from utils.logger import get_logger

logger = get_logger('report')

class ReportService:
    """Generates validation reports and output files."""

    def __init__(self, df: pd.DataFrame, results: Dict[str, List[ValidationError]]) -> None:
        self._df = df
        self._results = results

    """
        
    Notice — the constructor takes the **original DataFrame** and the **validation results**.
    It needs both to build the report: the original data to split into clean/flagged, and the errors to explain what went wrong.
    
    This is composition again — `ReportService` doesn't validate anything. It **consumes** what `ValidationService` produced.
    
    CSV → ValidationService → results → ReportService → output files
    """
    def generate_summary(self) -> pd.DataFrame:
        """Add validation columns to the original DataFrame."""
        df = self._df.copy()

        df['validation_status'] = df['transaction_id'].apply(
            lambda txn: 'CLEAN' if not self._results.get(txn, []) else 'FLAGGED'
        )

        df['error_count'] = df['transaction_id'].apply(
            lambda txn: len(self._results.get(txn, []))
        )

        df['error_codes'] = df['transaction_id'].apply(
            lambda txn: ', '.join(err.error_code for err in self._results.get(txn, []))
        )

        df['error_messages'] = df['transaction_id'].apply(
            lambda txn: ', '.join(str(err) for err in self._results.get(txn, []))
        )

        df['severity'] = df['transaction_id'].apply(
            lambda txn: self._get_worst_severity(self._results.get(txn, []))
        )

        return df

    # the helper
    @staticmethod
    def _get_worst_severity(errors: List[ValidationError]) -> str:
        """Return the highest severity from a list of errors."""
        from config.constants import SEVERITY_ORDER, Severity

        if not errors:
            return Severity.NONE

        return max(
            (err.severity for err in errors),
            key=lambda s: SEVERITY_ORDER.get(s, 0)
        )

    """
    Two things to notice:

    `self._df.copy()`** — never modify the original. Defensive programming, same philosophy as `frozen=True` and `_errors.copy()`.

    `_get_worst_severity`** — a transaction with 3 MEDIUM errors and 1 CRITICAL gets `CRITICAL`.
     The `max()` with `SEVERITY_ORDER` picks the highest. 
     That's your severity ranking from `constants.py` paying off.
    """

    def save_reports(self) -> None:
        """Split into clean/flagged and save to output directory."""
        summary = self.generate_summary()

        # Ensure output directory exists
        settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Save full report
        report_path = settings.OUTPUT_DIR / settings.REPORT_OUTPUT
        summary.to_csv(report_path, index=False)
        logger.info(f"Full report: {report_path}")

        # Save clean transactions
        clean = summary[summary['validation_status'] == 'CLEAN']
        clean_path = settings.OUTPUT_DIR / settings.VALID_OUTPUT
        clean.to_csv(clean_path, index=False)
        logger.info(f"Clean transactions: {len(clean)} → {clean_path}")

        # Save flagged transactions
        flagged = summary[summary['validation_status'] == 'FLAGGED']
        flagged_path = settings.OUTPUT_DIR / settings.FLAGGED_OUTPUT
        flagged.to_csv(flagged_path, index=False)
        logger.info(f"Flagged transactions: {len(flagged)} → {flagged_path}")












