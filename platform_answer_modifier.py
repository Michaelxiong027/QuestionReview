from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests


MODIFY_API = "https://api-internal.tipaipai.com/maliang-inner-service/jf/audit/modify"
CONTAINER_KEYS = (
    "label_containers",
    "cur_page_link_containers",
    "link_cur_page_containers",
)


class ModificationError(RuntimeError):
    pass


def read_authorization(path: Path) -> str:
    value = path.read_text(encoding="utf-8-sig").strip()
    if not value:
        raise ModificationError(f"Authorization file is empty: {path}")
    return value


def parse_job_id(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if parsed.fragment and "?" in parsed.fragment:
        query.update(parse_qs(parsed.fragment.split("?", 1)[1]))
    return str((query.get("job_id") or [""])[0])


def answer_items(container: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for key in ("answerInfo", "answerInfo2"):
        value = container.get(key)
        if isinstance(value, list):
            items.extend(item for item in value if isinstance(item, dict))
    independent = (container.get("answerIndependent") or {}).get("iAnswerInfo")
    if isinstance(independent, list):
        items.extend(item for item in independent if isinstance(item, dict))
    elif isinstance(independent, dict):
        items.append(independent)
    return items


def normalize(value: Any) -> str:
    return str(value if value is not None else "").strip()


def collect_wrappers(data: dict[str, Any]) -> list[dict[str, Any]]:
    wrappers: list[dict[str, Any]] = []
    for key in CONTAINER_KEYS:
        value = data.get(key) or []
        if isinstance(value, list):
            wrappers.extend(item for item in value if isinstance(item, dict))
    return wrappers


def find_container(
    wrappers: list[dict[str, Any]], sequence: str, link_id: str = ""
) -> dict[str, Any]:
    matches = [
        wrapper.get("labelContainer") or {}
        for wrapper in wrappers
        if normalize((wrapper.get("labelContainer") or {}).get("sequence"))
        == normalize(sequence)
    ]
    if link_id:
        matches = [
            container
            for container in matches
            if any(normalize(item.get("linkId")) == link_id for item in answer_items(container))
        ]
    if len(matches) != 1:
        raise ModificationError(
            f"Question sequence {sequence!r} matched {len(matches)} containers"
        )
    return matches[0]


def apply_updates(
    wrappers: list[dict[str, Any]], updates: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    applied: list[dict[str, Any]] = []
    for update in updates:
        sequence = normalize(update.get("sequence"))
        if not sequence:
            raise ModificationError("answer_updates item is missing sequence")
        link_id = normalize(update.get("link_id"))
        container = find_container(wrappers, sequence, link_id)
        answers = answer_items(container)
        if link_id:
            matches = [item for item in answers if normalize(item.get("linkId")) == link_id]
            if len(matches) != 1:
                raise ModificationError(
                    f"Sequence {sequence!r}, link_id {link_id!r} matched {len(matches)} answers"
                )
            answer = matches[0]
            answer_index = answers.index(answer) + 1
        else:
            answer_index = int(update.get("answer_index", 1))
            if answer_index < 1 or answer_index > len(answers):
                raise ModificationError(
                    f"Sequence {sequence!r} has {len(answers)} answers; "
                    f"answer_index={answer_index} is invalid"
                )
            answer = answers[answer_index - 1]

        current = normalize(answer.get("answerText"))
        expected = update.get("old_answer")
        if expected is not None and current != normalize(expected):
            raise ModificationError(
                f"Sequence {sequence!r}, answer {answer_index}: platform answer "
                f"{current!r} does not match expected {normalize(expected)!r}"
            )
        new_text = normalize(update.get("new_answer"))
        if not new_text:
            raise ModificationError(
                f"Sequence {sequence!r}, answer {answer_index}: new_answer is empty"
            )
        answer["answerText"] = new_text
        answer["answerRichText"] = str(
            update.get("new_answer_rich_text", update.get("new_answer_rich", new_text))
        )
        applied.append(
            {
                "sequence": sequence,
                "answer_index": answer_index,
                "link_id": answer.get("linkId"),
                "old_answer": current,
                "new_answer": new_text,
            }
        )
    return applied


def build_modify_payload(
    manifest_item: dict[str, Any],
    platform_response: dict[str, Any],
    updates: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data = platform_response.get("data") or {}
    wrappers = collect_wrappers(data)
    if not isinstance(wrappers, list) or not wrappers:
        raise ModificationError("Platform response has no answer containers")
    applied = apply_updates(wrappers, updates)
    job_id = parse_job_id(normalize(manifest_item.get("url")))
    if not job_id:
        job_id = normalize(wrappers[0].get("jobId"))
    if not job_id:
        raise ModificationError("Unable to determine job_id")
    payload = {
        "book_id": int(manifest_item.get("book_id") or data.get("book_id")),
        "page_id": int(manifest_item.get("page_id") or data.get("page_id")),
        "job_id": job_id,
        "page_num": data.get("page_num", manifest_item.get("page_number")),
        "ques_count": data.get("ques_count", len(wrappers)),
    }
    for key in CONTAINER_KEYS:
        key_wrappers = data.get(key) or []
        if not isinstance(key_wrappers, list) or not key_wrappers:
            continue
        payload[key] = [
            json.dumps(
                wrapper.get("labelContainer") or {},
                ensure_ascii=False,
                separators=(",", ":"),
            )
            for wrapper in key_wrappers
            if isinstance(wrapper, dict)
        ]
    return payload, applied


def request_hash(payload: dict[str, Any], applied: list[dict[str, Any]]) -> str:
    relevant = {
        "page_id": payload["page_id"],
        "book_id": payload["book_id"],
        "updates": applied,
    }
    raw = json.dumps(relevant, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def submit_payload(payload: dict[str, Any], authorization: str) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    response = requests.post(
        MODIFY_API,
        headers={
            "Authorization": authorization,
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Mozilla/5.0",
        },
        data=body,
        timeout=60,
    )
    response.raise_for_status()
    body = response.json()
    if body.get("error_code") not in (None, 0):
        raise ModificationError(body.get("error_msg") or "Modify API returned an error")
    return body


def apply_result_modifications(
    results_path: Path,
    run_dir: Path,
    authorization_path: Path,
    *,
    dry_run: bool = False,
    force_rows: set[int] | None = None,
) -> dict[str, int]:
    results = load_json(results_path)
    manifest = load_json(run_dir / "manifest.json")
    by_row = {int(item["row"]): item for item in manifest}
    authorization = "" if dry_run else read_authorization(authorization_path)
    journal_path = results_path.parent / "platform_modifications.json"
    journal = load_json(journal_path) if journal_path.exists() else {}
    counts = {"submitted": 0, "skipped": 0, "failed": 0, "dry_run": 0}
    force_rows = force_rows or set()

    for row_text, result in sorted(results.items(), key=lambda pair: int(pair[0])):
        updates = result.get("answer_updates") or []
        if not updates:
            continue
        row = int(row_text)
        item = by_row.get(row)
        if not item or item.get("status") != "downloaded":
            counts["failed"] += 1
            journal[row_text] = {"status": "failed", "error": "Downloaded page not found"}
            continue
        page_dir = Path(item["page_dir"])
        try:
            platform_response = load_json(page_dir / "platform_response.json")
            payload, applied = build_modify_payload(item, platform_response, updates)
            digest = request_hash(payload, applied)
            previous = journal.get(row_text) or {}
            if (
                row not in force_rows
                and previous.get("status") == "success"
                and previous.get("request_hash") == digest
            ):
                counts["skipped"] += 1
                continue
            write_json(page_dir / "platform_modify_request.json", payload)
            if dry_run:
                counts["dry_run"] += 1
                journal[row_text] = {
                    "status": "dry_run",
                    "request_hash": digest,
                    "updates": applied,
                }
                continue
            response = submit_payload(payload, authorization)
            write_json(page_dir / "platform_modify_response.json", response)
            counts["submitted"] += 1
            journal[row_text] = {
                "status": "success",
                "request_hash": digest,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "updates": applied,
                "response_file": str(page_dir / "platform_modify_response.json"),
            }
        except Exception as exc:
            counts["failed"] += 1
            journal[row_text] = {
                "status": "failed",
                "error": str(exc),
                "failed_at": datetime.now(timezone.utc).isoformat(),
            }
        finally:
            write_json(journal_path, journal)
    return counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply structured Codex answer corrections to the platform."
    )
    parser.add_argument("--results", default="_codex_review/results.json")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--authorization", default="authorization.txt")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--force-row",
        action="append",
        type=int,
        default=[],
        help="Re-submit a row even when the journal already has the same successful request hash.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path.cwd()
    counts = apply_result_modifications(
        (root / args.results).resolve(),
        (root / args.run_dir).resolve(),
        (root / args.authorization).resolve(),
        dry_run=args.dry_run,
        force_rows=set(args.force_row),
    )
    print(json.dumps(counts, ensure_ascii=False), flush=True)
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
