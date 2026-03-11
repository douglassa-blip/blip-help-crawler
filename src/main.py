from __future__ import annotations

import argparse
from pathlib import Path

from src.pipelines.export_full import run_full_export
from src.pipelines.export_incremental import run_incremental_export
from src.utils.logging import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export BLiP Help Center data from sitemap")
    parser.add_argument("--mode", choices=["full", "incremental"], default="full")
    parser.add_argument("--locale", default="pt-br")
    parser.add_argument("--output-root", default="data")
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()

    if args.mode == "incremental":
        run_incremental_export(output_root=Path(args.output_root), locale=args.locale)
    else:
        run_full_export(output_root=Path(args.output_root), locale=args.locale)


if __name__ == "__main__":
    main()
