import logging

import pandas as pd

logger = logging.getLogger(__name__)


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: list[str] | None = None,
    numeric_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Check required columns and coerce numeric columns.

    Rows whose value in a numeric column is present but not numeric are
    removed (blank/missing values are kept for later missing-value handling).
    Raises ValueError if a required column is absent.
    """
    required_columns = required_columns or []
    numeric_columns = numeric_columns or []

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    rows_before = len(df)
    result = df.copy()
    for col in numeric_columns:
        if col not in result.columns:
            raise ValueError(f"Numeric column not found: {col}")
        converted = pd.to_numeric(result[col], errors="coerce")
        invalid = converted.isna() & result[col].notna()
        for value in result.loc[invalid, col].unique():
            logger.warning("Invalid value in %s: %s", col, value)
        result = result.loc[~invalid].copy()
        result[col] = converted.loc[result.index]

    logger.debug("Validation: %s → %s rows", rows_before, len(result))
    return result.reset_index(drop=True)
