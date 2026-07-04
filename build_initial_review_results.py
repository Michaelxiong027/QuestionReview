from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PLACEHOLDER_ANSWERS = {"略略略", "鐣ョ暐鐣?", "鐣ョ暐鐣�"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a conservative initial Codex review results file."
    )
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output", default="_codex_review/results.json")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def as_text(value: Any) -> str:
    return str(value if value is not None else "").strip()


def has_placeholder_answer(item: dict[str, Any]) -> bool:
    for question in item.get("questions") or []:
        for answer in question.get("platform_answers") or []:
            if as_text(answer) in PLACEHOLDER_ANSWERS:
                return True
    return False


def first_answer_image(run_dir: Path, item: dict[str, Any]) -> str | None:
    position = int(item["position"])
    matches = sorted(run_dir.glob(f"url_{position:04d}_*/answer/*.png"))
    if matches:
        return str(matches[0])
    for question in item.get("questions") or []:
        path = question.get("answer_image")
        if path:
            candidate = Path(as_text(path))
            if candidate.exists():
                return str(candidate)
    return None


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    output_path = Path(args.output)
    manifest = load_json(run_dir / "manifest.json")
    results: dict[str, dict[str, Any]] = {}

    for item in manifest:
        row = int(item["row"])
        question_count = int(item.get("question_count") or 0)
        if item.get("status") != "downloaded":
            results[str(row)] = {
                "status": "需人工处理",
                "correct_answers": "",
                "analysis": f"下载失败：{item.get('error', '')}",
                "error_images": [],
            }
        elif question_count == 0:
            results[str(row)] = {
                "status": "存在问题，需人工补充答案",
                "correct_answers": "",
                "analysis": "平台未返回可批改答案题块，无法进行平台答案对比；需人工检查是否删框或补充答案。",
                "error_images": [],
            }
        elif has_placeholder_answer(item):
            image = first_answer_image(run_dir, item)
            results[str(row)] = {
                "status": "存在问题，需人工补充答案",
                "correct_answers": "",
                "analysis": "平台答案包含“略略略”占位答案；按 README 规则不作为平台答案错误对比项，需人工补充标准答案。",
                "error_images": [image] if image else [],
            }
        else:
            results[str(row)] = {
                "status": "待视觉复核",
                "correct_answers": "",
                "analysis": "已下载平台报文和题目截图；尚未完成逐题视觉复核，未确认平台答案错误。",
                "error_images": [],
            }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    counts: dict[str, int] = {}
    for result in results.values():
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    print(json.dumps(counts, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
