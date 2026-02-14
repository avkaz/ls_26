import os
import sys

from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
)
