from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build visual review contact sheets.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--results", default="_codex_review/results.json")
    parser.add_argument("--out-dir", default="_codex_review/contact_sheets")
    parser.add_argument("--positions", nargs="*", type=int)
    parser.add_argument("--limit", type=int, default=10)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def font(size: int) -> ImageFont.ImageFont:
    for p in ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/arial.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def fit(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    scale = min(max_w / img.width, max_h / img.height, 1.0)
    return img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))))


def page_dir_for(run_dir: Path, position: int) -> Path:
    matches = sorted(run_dir.glob(f"url_{position:04d}_*"))
    if len(matches) != 1:
        raise FileNotFoundError(f"position {position} matched {len(matches)} dirs")
    return matches[0]


def build_sheet(run_dir: Path, item: dict[str, Any], out_dir: Path) -> Path:
    position = int(item["position"])
    page_dir = page_dir_for(run_dir, position)
    source = Image.open(page_dir / "source_page.jpg").convert("RGB")
    answers = sorted((page_dir / "answer").glob("*.png"))
    title_h = 56
    margin = 18
    gap = 14
    source_w = 760
    sheet_w = 2200
    source_h = 1500
    thumb_w = 420
    thumb_h = 280
    cols = 3
    rows = max(1, math.ceil(len(answers) / cols))
    sheet_h = title_h + margin * 2 + max(source_h, rows * (thumb_h + 42 + gap))
    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)
    title = (
        f"pos {position} / row {item.get('row')} / page {item.get('page_number')} / "
        f"page_id {item.get('page_id')} / questions {item.get('question_count')}"
    )
    draw.text((margin, 14), title, fill=(0, 0, 0), font=font(26))
    src = fit(source, source_w, source_h)
    sheet.paste(src, (margin, title_h + margin))
    draw.rectangle(
        (margin, title_h + margin, margin + src.width, title_h + margin + src.height),
        outline=(80, 80, 80),
        width=2,
    )
    x0 = margin + source_w + 28
    y0 = title_h + margin
    for idx, path in enumerate(answers):
        img = Image.open(path).convert("RGB")
        thumb = fit(img, thumb_w, thumb_h)
        col = idx % cols
        row = idx // cols
        x = x0 + col * (thumb_w + gap)
        y = y0 + row * (thumb_h + 42 + gap)
        draw.text((x, y), path.name, fill=(0, 0, 0), font=font(18))
        sheet.paste(thumb, (x, y + 28))
        draw.rectangle((x, y + 28, x + thumb.width, y + 28 + thumb.height), outline=(40, 40, 40), width=1)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"page_{position:04d}_row_{item.get('row')}.jpg"
    sheet.save(out, quality=92)
    return out


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    results = load_json(Path(args.results))
    manifest = load_json(run_dir / "manifest.json")
    if args.positions:
        wanted = set(args.positions)
        items = [item for item in manifest if int(item["position"]) in wanted]
    else:
        items = [
            item
            for item in manifest
            if (results.get(str(item["row"])) or {}).get("status") == "待视觉复核"
        ][: args.limit]
    for item in items:
        print(build_sheet(run_dir, item, Path(args.out_dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
