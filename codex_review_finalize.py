from __future__ import annotations

import argparse
import json
from pathlib import Path

from codex_visual_review_writer import load_results, write_workbook
from platform_answer_modifier import apply_result_modifications


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Submit Codex answer corrections and write review results to Excel."
    )
    parser.add_argument("--excel", default="questions.xlsx")
    parser.add_argument("--results", default="_codex_review/results.json")
    parser.add_argument("--output", help="Output workbook; defaults to overwriting --excel")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--authorization", default="authorization.txt")
    parser.add_argument(
        "--dry-run-platform-modifications",
        action="store_true",
        help="Validate and save modify payloads without sending them.",
    )
    parser.add_argument(
        "--skip-platform-modifications",
        action="store_true",
        help="Only write Excel; do not process answer_updates.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path.cwd()
    source = (root / args.excel).resolve()
    destination = (root / (args.output or args.excel)).resolve()
    results_path = (root / args.results).resolve()
    modification_failed = False

    if not args.skip_platform_modifications:
        counts = apply_result_modifications(
            results_path,
            (root / args.run_dir).resolve(),
            (root / args.authorization).resolve(),
            dry_run=args.dry_run_platform_modifications,
        )
        print(
            f"Platform modifications: {json.dumps(counts, ensure_ascii=False)}",
            flush=True,
        )
        modification_failed = counts["failed"] > 0

    results = load_results(results_path)
    write_workbook(source, destination, results)
    print(f"Wrote {len(results)} review records to {destination}", flush=True)
    return 1 if modification_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

