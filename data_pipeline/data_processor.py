import logging

import pandas as pd

logger = logging.getLogger(__name__)


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    result = df.drop_duplicates().reset_index(drop=True)
    logger.debug("remove_duplicates: %s → %s rows", before, len(result))
    return result


def handle_missing(df: pd.DataFrame, axis: str = "rows") -> pd.DataFrame:
    before = len(df)
    if axis == "rows":
        result = df.dropna(axis=0).reset_index(drop=True)
    elif axis == "columns":
        result = df.dropna(axis=1)
    else:
        raise ValueError(f"Unsupported missing-value axis: {axis!r}")
    logger.debug("handle_missing: %s → %s rows", before, len(result))
    return result


def remove_outliers(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "iqr",
    threshold: float = 1.5,
) -> pd.DataFrame:
    if method not in ("iqr", "zscore"):
        raise ValueError(f"Unsupported outlier method: {method!r}")
    before = len(df)
    result = df.copy()
    for col in columns:
        if col not in result.columns:
            raise ValueError(f"Outlier column not found: {col}")
        series = pd.to_numeric(result[col], errors="coerce")
        if method == "iqr":
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            keep = series.between(q1 - threshold * iqr, q3 + threshold * iqr)
        else:
            std = series.std()
            keep = (
                pd.Series(True, index=series.index)
                if not std
                else ((series - series.mean()).abs() / std) <= threshold
            )
        result = result.loc[keep | series.isna()]
    result = result.reset_index(drop=True)
    logger.debug("remove_outliers (%s): %s → %s rows", method, before, len(result))
    return result


def process_data(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Apply duplicate, missing-value and outlier steps from a config dict."""
    settings = config.get("processing", config)
    result = df.copy()

    if settings.get("remove_duplicates", False):
        result = remove_duplicates(result)

    missing = settings.get("missing", {})
    if missing.get("enabled", False):
        result = handle_missing(result, axis=missing.get("axis", "rows"))

    outliers = settings.get("outliers", {})
    if outliers.get("enabled", False):
        result = remove_outliers(
            result,
            columns=outliers.get("columns", []),
            method=outliers.get("method", "iqr"),
            threshold=outliers.get("threshold", 1.5),
        )
    return result
