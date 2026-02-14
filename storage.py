from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from config.parameters import BASE_OUTPUT_DIR
from schemas import MatchReport

BASE_DIR = BASE_OUTPUT_DIR
BASE_DIR.mkdir(exist_ok=True, parents=True)


def save_match_report(result: MatchReport, source_url: str) -> Path:
    """
    Save full MatchReport statistics to a JSON file.

    One file per run, timestamped.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_home = (result.home_team or "unknown").replace(" ", "_")
    safe_away = (result.away_team or "unknown").replace(" ", "_")

    filename = f"{timestamp}_{safe_home}_vs_{safe_away}.json"
    path = BASE_DIR / filename

    payload = {
        "source_url": source_url,
        "saved_at_utc": timestamp,
        "data": result.model_dump(),
    }

    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        logger.success(f"Match statistics saved to {path}")
        return path

    except Exception:
        logger.exception("Failed to save match report to file")
        raise
