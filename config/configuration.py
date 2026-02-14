"""Application configuration and logging setup."""

import os
import sys
from typing import Final

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Tool name used for function/tool calling
TOOL_NAME: Final[str] = "submit_match_report"

run_mode = os.getenv("MODE", "prod").lower()

if run_mode == "dev":
    log_level = "DEBUG"
elif run_mode == "prod":
    log_level = "INFO"
else:
    raise ValueError(
        f"Invalid MODE '{run_mode}' in environment variables. Expected 'dev' or 'prod'."
    )

logger.remove()
logger.add(sys.stderr, level=log_level)
