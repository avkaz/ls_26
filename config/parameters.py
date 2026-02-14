from pathlib import Path
from typing import Final

# Model to use for OpenAI ("gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini", "gpt-4o", "gpt-5-mini", etc.)
MODEL: Final[str] = "gpt-4.1-mini"

# Default temperature for generation
TEMPERATURE: Final[float] = 0.2

# Length of final report in words (approximate, not strict)
REPORT_LENGTH_WORDS: Final[int] = 300

# Environment variable name that holds the OpenAI API key
API_ENV_VAR: Final[str] = "OPENAI_API_KEY"

# Playwright navigation / fetch timeout (milliseconds)
DEFAULT_TIMEOUT_MS: Final[int] = 30_000

# Maximum characters to extract from cleaned HTML
MAX_CHARS: Final[int] = 8000

# Relative path segment used to build stats URLs on Livesport
STATS_PATH: Final[str] = "/prehled/stats/celkem/"

# Output directory for saved match reports
BASE_OUTPUT_DIR: Final[Path] = Path("outputs")

# Default logging level (used by configuration setup)
DEFAULT_LOG_LEVEL: Final[str] = "INFO"
