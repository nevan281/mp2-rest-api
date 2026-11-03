import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def create_cleaning_report(before: pd.DataFrame, after: pd.DataFrame) -> dict[str, int]:
    """Compare two DataFrames and summarize rows/columns removed."""
    return {
        "rows_before": len(before),
        "rows_after": len(after),
        "rows_removed": len(before) - len(after),
        "columns_before": len(before.columns),
        "columns_after": len(after.columns),
        "columns_removed": len(before.columns) - len(after.columns),
    }


def save_csv(df: pd.DataFrame, path) -> None:
    """Write a DataFrame to CSV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.debug("Saved %s rows to %s", len(df), path)
