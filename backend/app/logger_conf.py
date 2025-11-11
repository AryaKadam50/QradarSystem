"""
Application logger configuration - logs to file and console.
Uses syslog forwarding to QRadar if QRADAR_HOST is configured.
"""
import logging
import os
from logging.handlers import SysLogHandler
from pathlib import Path

# Log file path - use writable directory
log_dir = Path.home() / '.qradar_logs'
log_dir.mkdir(exist_ok=True)
LOG_FILE = str(log_dir / 'secure_app.log')

QRADAR_HOST = os.getenv("QRADAR_HOST")  # e.g., 10.0.0.5
QRADAR_PORT = int(os.getenv("QRADAR_PORT", "514"))

logger = logging.getLogger("secure_app")
logger.setLevel(logging.INFO)

# File handler
try:
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)
except Exception as e:
    print(f"Warning: Could not create file logger: {e}")

# Console handler (always works)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(ch)

# Syslog Handler to forward to QRadar if QRADAR_HOST provided
if QRADAR_HOST:
    try:
        sh = SysLogHandler(address=(QRADAR_HOST, QRADAR_PORT))
        sh.setFormatter(logging.Formatter("%(asctime)s secure_app: %(levelname)s %(message)s"))
        logger.addHandler(sh)
    except Exception as e:
        logger.warning(f"Could not create SysLogHandler: {e}")
