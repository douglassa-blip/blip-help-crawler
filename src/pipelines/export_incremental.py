from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from src.pipelines.export_full import run_full_export


def run_incremental_export(raw_articles: Iterable[dict], output_root: Path, source_used: str, updated_since: datetime) -> dict:
    filtered = []
    for article in raw_articles:
        updated_at = article.get("updated_at")
        if not updated_at:
            continue
        if isinstance(updated_at, str):
            parsed = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        else:
            parsed = updated_at
        if parsed >= updated_since:
            filtered.append(article)

    return run_full_export(filtered, output_root=output_root, source_used=source_used)
