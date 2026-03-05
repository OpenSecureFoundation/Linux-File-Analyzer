# src/FileAnalyzer/logger.py

import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "file_analyzer.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

def get_logger(name="FileAnalyzer"):
    return logging.getLogger(name)
