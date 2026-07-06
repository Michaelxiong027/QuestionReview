from __future__ import annotations

import argparse
import json
from pathlib import Path

from qr_audio_extractor import scan_page


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan QR/audio only for pages missing a QR manifest.")
    parser.add_argument("--run-dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    pages: list[dict] = []
    counts = {"pages": 0, "qr_pages": 0, "audio_pages": 0, "unresolved_pages": 0, "skipped": 0}
    for item in manifest:
        if item.get("status") != "downloaded":
            continue
        page_dir = Path(item["page_dir"])
        page_manifest = page_dir / "qr_audio_manifest.json"
        if page_manifest.exists():
            page = json.loads(page_manifest.read_text(encoding="utf-8"))
            counts["skipped"] += 1
        else:
            page = scan_page(page_dir)
            print(f"[scan] QR/audio: {page['status']} - {page['source_page']}", flush=True)
        page.update(position=item.get("position"), row=item.get("row"))
        pages.append(page)
        counts["pages"] += 1
        if page["status"] != "no_qr":
            counts["qr_pages"] += 1
        if page["status"] == "audio_downloaded":
            counts["audio_pages"] += 1
        elif page["status"] == "qr_unresolved":
            counts["unresolved_pages"] += 1
    output = {"counts": counts, "pages": pages}
    (run_dir / "qr_audio_manifest.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(counts, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
