from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from src.pipelines.export_full import run_full_export
from src.utils.files import write_json

logger = logging.getLogger(__name__)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def run_incremental_export(output_root: Path, locale: str | None = None) -> dict:
    state_path = output_root / "state.json"
    last_run: datetime | None = None

    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        last_run = _parse_datetime(state.get("last_run"))

    manifest = run_full_export(output_root=output_root, locale=locale)

    exports_jsonl = output_root / "exports" / "articles.jsonl"
    if last_run and exports_jsonl.exists():
        rows = [json.loads(line) for line in exports_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
        filtered = []
        for row in rows:
            updated_at = _parse_datetime(row.get("updated_at"))
            if updated_at and updated_at > last_run:
                filtered.append(row)
        from src.utils.files import write_jsonl

        write_jsonl(exports_jsonl, filtered)
        manifest["success"] = len(filtered)

    now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    write_json(state_path, {"last_run": now_iso})
    write_json(output_root / "exports" / "state.json", {"last_run": now_iso})
    return manifest


if __name__ == "__main__":
    import argparse

    from src.utils.logging import configure_logging

    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--locale", default="pt-br")
    parser.add_argument("--output-root", default="data")
    args = parser.parse_args()

    result = run_incremental_export(Path(args.output_root), locale=args.locale)
    logger.info("Incremental export complete: %s", result)
