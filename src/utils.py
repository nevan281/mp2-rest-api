import logging
import sys


def setup_logging(verbose: bool = False) -> None:
    """Configure root logging. DEBUG when verbose, otherwise INFO."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
