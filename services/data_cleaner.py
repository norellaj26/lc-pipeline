import pandas as pd
from config.constants import UNICODE_REPLACEMENTS, COLS_UPPERCASE

class DataCleaner:
    """Cleans raw CSV data before validation."""

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Public entry point. Returns a NEW cleaned DataFrame."""
        cleaned = df.copy()
        self._clean_unicode(cleaned)
        self._clean_whitespace(cleaned)
        self._clean_case(cleaned)

        return cleaned

    def _clean_unicode(self, df: pd.DataFrame) -> None:
        """Replace unicode characters with standard equivalents."""
        for col in df.select_dtypes(include='object').columns:
            for old_char, new_char in UNICODE_REPLACEMENTS.items():
                df[col] = df[col].str.replace(old_char, new_char, regex=False)


    # With regex=False you're telling pandas: treat this as a plain literal string, not a pattern. Without it, a character
    # like '(' in your replacement map would crash or behave unexpectedly because '(' means "start of a group" in regex.

    def _clean_whitespace(self, df: pd.DataFrame) -> None:
        """Strip and collapse whitespace in all string columns."""
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].str.strip()
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True)

    # '\u200B': '',   # Zero-width space (remove!) That one maps to empty string, not a space. \s does NOT match \u200B


    def _clean_case(self, df: pd.DataFrame) -> None:
        """Uppercase columns that need case normalization."""
        for col in COLS_UPPERCASE:
            if col in df.columns:
                df[col] = df[col].str.upper()