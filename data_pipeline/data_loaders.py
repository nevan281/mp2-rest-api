import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def load_csv(path) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    df = pd.read_csv(path)
    logger.debug("Loaded %s: %s rows", path, len(df))
    return df
