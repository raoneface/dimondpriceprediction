import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


# Keep logs in the project-level logs folder irrespective of current working directory.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Use a daily log file to avoid fragmented files from debug reloads.
LOG_FILE_PATH = os.path.join(LOGS_DIR, f"{datetime.now().strftime('%m_%d_%Y')}.log")

LOG_LEVEL_NAME = os.getenv("LOG_LEVEL", "DEBUG").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME, logging.DEBUG)

LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s:%(lineno)d - %(message)s"
formatter = logging.Formatter(LOG_FORMAT)

file_handler = RotatingFileHandler(
    LOG_FILE_PATH,
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8",
)
file_handler.setFormatter(formatter)
file_handler.setLevel(LOG_LEVEL)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(LOG_LEVEL)

logging.basicConfig(
    level=LOG_LEVEL,
    handlers=[file_handler, stream_handler],
    force=True,
)

logging.getLogger("werkzeug").setLevel(logging.INFO)
logging.getLogger(__name__).info(
    "Logger initialized | level=%s | file=%s",
    LOG_LEVEL_NAME,
    LOG_FILE_PATH,
)