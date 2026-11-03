# data_processor.py
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def remove_duplicates(df):
    """Remove duplicate rows."""
    before = len(df)
    result = df.drop_duplicates()
    logger.debug("remove_duplicates: %s → %s rows", before, len(result))
    return result


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis == "rows":
        before = len(df)
        result = df.dropna(axis=0)
        logger.debug("handle_missing: %s → %s rows", before, len(result))
    elif axis == "columns":
        before = len(df.columns)
        result = df.dropna(axis=1)
        logger.debug("handle_missing: %s → %s columns", before, len(result.columns))
    else:
        logger.error("Unsupported axis for handle_missing: %s", axis)
        raise ValueError(f"Unsupported axis for handle_missing: {axis}")
    return result


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ("iqr", "zscore"):
        logger.error("Unsupported outlier method: %s", method)
        raise ValueError(f"Unsupported outlier method: {method}")

    result = df
    for col in columns:
        if col not in result.columns:
            logger.warning("Column not found: %s", col)
            continue
        if not pd.api.types.is_numeric_dtype(result[col]):
            logger.warning("Column is not numeric: %s", col)
            continue

        series = result[col]
        if method == "iqr":
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            is_outlier = (series < lower) | (series > upper)
        else:  # zscore
            std = series.std()
            if std == 0 or pd.isna(std):
                is_outlier = pd.Series(False, index=series.index)
            else:
                is_outlier = ((series - series.mean()) / std).abs() > threshold

        removed = int(is_outlier.sum())
        result = result[~is_outlier]
        logger.debug(
            "%s: method=%s, threshold=%s, removed=%s",
            col, method, threshold, removed,
        )
    return result


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    settings = config["processing"]

    if settings.get("remove_duplicates", False):
        df = remove_duplicates(df)

    missing = settings.get("missing", {})
    if missing.get("enabled", False):
        df = handle_missing(df, axis=missing.get("axis", "rows"))

    outliers = settings.get("outliers", {})
    if outliers.get("enabled", False):
        df = remove_outliers(
            df,
            columns=outliers.get("columns", []),
            method=outliers.get("method", "iqr"),
            threshold=outliers.get("threshold", 1.5),
        )
    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    return {
        "rows_before": len(df_before),
        "rows_after": len(df_after),
        "rows_removed": len(df_before) - len(df_after),
        "columns_before": len(df_before.columns),
        "columns_after": len(df_after.columns),
        "columns_removed": len(df_before.columns) - len(df_after.columns),
    }
