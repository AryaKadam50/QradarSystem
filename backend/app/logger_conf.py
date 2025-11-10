# backend/app/logger_conf.py
import logging
import os
from logging.handlers import SysLogHandler

LOG_FILE = os.getenv("APP_LOG_FILE", "/var/log/secure_app.log")
QRADAR_HOST = os.getenv("QRADAR_HOST")  # e.g., 10.0.0.5
QRADAR_PORT = int(os.getenv("QRADAR_PORT", "514"))

logger = logging.getLogger("secure_app")
logger.setLevel(logging.INFO)

# File handler
fh = logging.FileHandler(LOG_FILE)
fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(fh)

# Syslog Handler to forward to QRadar if QRADAR_HOST provided
if QRADAR_HOST:
    try:
        sh = SysLogHandler(address=(QRADAR_HOST, QRADAR_PORT))
        sh.setFormatter(logging.Formatter("%(asctime)s secure_app: %(levelname)s %(message)s"))
        logger.addHandler(sh)
    except Exception as e:
        logger.warning(f"Could not create SysLogHandler: {e}")
