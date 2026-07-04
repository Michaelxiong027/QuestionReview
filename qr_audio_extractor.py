from __future__ import annotations

import argparse
import html
import json
import mimetypes
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import cv2
import numpy as np
import requests


AUDIO_EXTENSIONS = {".mp3", ".m4a", ".aac", ".wav", ".ogg", ".flac", ".mp4"}
AUDIO_URL_RE = re.compile(
    r"https?://[^\s\"'<>]+?\.(?:mp3|m4a|aac|wav|ogg|flac|mp4)(?:\?[^\s\"'<>]*)?",
    re.IGNORECASE,
)
ATTRIBUTE_RE = re.compile(
    r"(?:src|href|data-src|data-url)\s*=\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def read_image(path: Path) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(path.read_bytes(), np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Unable to read image: {path}")
    return image


def decode_qr_codes(path: Path) -> list[dict[str, Any]]:
    image = read_image(path)
    detector = cv2.QRCodeDetector()
    decoded: list[dict[str, Any]] = []

    def collect(values: Any, points: Any, scale: float = 1.0) -> None:
        if points is None:
            return
        for value, polygon in zip(values, points):
            value = str(value or "").strip()
            if not value or any(item["value"] == value for item in decoded):
                continue
            decoded.append(
                {
                    "value": value,
                    "points": (np.asarray(polygon) / scale).round(2).tolist(),
                }
            )

    try:
        ok, values, points, _ = detector.detectAndDecodeMulti(image)
        if ok:
            collect(values, points)
    except cv2.error:
        pass

    if not decoded:
        value, points, _ = detector.detectAndDecode(image)
        if value and points is not None:
            collect([value], points)

    if not decoded:
        enlarged = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        try:
            ok, values, points, _ = detector.detectAndDecodeMulti(enlarged)
            if ok:
                collect(values, points, scale=2.0)
        except cv2.error:
            pass
    return decoded


def is_audio_url(url: str) -> bool:
    return Path(urlparse(url).path).suffix.lower() in AUDIO_EXTENSIONS


def audio_candidates(html_text: str, base_url: str) -> list[str]:
    text = html.unescape(html_text).replace("\\/", "/")
    values = AUDIO_URL_RE.findall(text)
    for candidate in ATTRIBUTE_RE.findall(text):
        absolute = urljoin(base_url, html.unescape(candidate))
        if is_audio_url(absolute):
            values.append(absolute)
    unique: list[str] = []
    for value in values:
        value = value.rstrip("\\,);]")
        if value not in unique:
            unique.append(value)
    return unique


def extension_for(response: requests.Response, url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in AUDIO_EXTENSIONS:
        return suffix
    content_type = (response.headers.get("content-type") or "").split(";", 1)[0]
    return mimetypes.guess_extension(content_type) or ".audio"


def download_audio(
    session: requests.Session, url: str, destination_stem: Path
) -> tuple[Path, dict[str, Any]]:
    response = session.get(url, timeout=90, allow_redirects=True)
    response.raise_for_status()
    content_type = (response.headers.get("content-type") or "").lower()
    if not content_type.startswith("audio/") and not is_audio_url(response.url):
        raise RuntimeError(f"Not an audio response: {content_type or 'unknown'}")
    path = destination_stem.with_suffix(extension_for(response, response.url))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)
    return path, {
        "audio_url": response.url,
        "audio_file": str(path),
        "content_type": content_type,
        "bytes": len(response.content),
    }


def resolve_qr_value(
    value: str, audio_dir: Path, index: int
) -> dict[str, Any]:
    result: dict[str, Any] = {"qr_value": value, "status": "unresolved"}
    if not value.lower().startswith(("http://", "https://")):
        result["reason"] = "QR content is not an HTTP URL"
        return result
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    try:
        if is_audio_url(value):
            path, details = download_audio(session, value, audio_dir / f"audio_{index:03d}")
            result.update(details)
            result["status"] = "downloaded"
            return result

        response = session.get(value, timeout=45, allow_redirects=True)
        result["final_url"] = response.url
        result["http_status"] = response.status_code
        content_type = (response.headers.get("content-type") or "").lower()
        result["content_type"] = content_type
        if response.ok and (content_type.startswith("audio/") or is_audio_url(response.url)):
            path = (audio_dir / f"audio_{index:03d}").with_suffix(
                extension_for(response, response.url)
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(response.content)
            result.update(audio_url=response.url, audio_file=str(path), bytes=len(response.content))
            result["status"] = "downloaded"
            return result

        if response.ok and ("html" in content_type or response.text):
            candidates = audio_candidates(response.text, response.url)
            result["audio_candidates"] = candidates
            for candidate_index, candidate in enumerate(candidates, start=1):
                try:
                    path, details = download_audio(
                        session,
                        candidate,
                        audio_dir / f"audio_{index:03d}_{candidate_index:02d}",
                    )
                    result.setdefault("downloads", []).append(details)
                except Exception as exc:
                    result.setdefault("candidate_errors", []).append(
                        {"url": candidate, "error": str(exc)}
                    )
            if result.get("downloads"):
                result["status"] = "downloaded"
                return result

        host = (urlparse(response.url).hostname or "").lower()
        if host.endswith("weixin.qq.com") or host.endswith("weixin110.qq.com"):
            result["reason"] = "WeChat-gated QR; no public audio URL is exposed"
        else:
            result["reason"] = "No downloadable audio resource found"
    except Exception as exc:
        result["reason"] = str(exc)
    return result


def scan_page(page_dir: Path) -> dict[str, Any]:
    source = page_dir / "source_page.jpg"
    record: dict[str, Any] = {"source_page": str(source), "qr_codes": []}
    if not source.exists():
        record["status"] = "missing_source"
        return record
    qr_codes = decode_qr_codes(source)
    record["qr_codes"] = qr_codes
    if not qr_codes:
        record["status"] = "no_qr"
    else:
        audio_dir = page_dir / "audio"
        resolutions = [
            resolve_qr_value(qr["value"], audio_dir, index)
            for index, qr in enumerate(qr_codes, start=1)
        ]
        record["resolutions"] = resolutions
        record["status"] = (
            "audio_downloaded"
            if any(item["status"] == "downloaded" for item in resolutions)
            else "qr_unresolved"
        )
    (page_dir / "qr_audio_manifest.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return record


def scan_run(run_dir: Path) -> dict[str, Any]:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    pages: list[dict[str, Any]] = []
    counts = {"pages": 0, "qr_pages": 0, "audio_pages": 0, "unresolved_pages": 0}
    for item in manifest:
        if item.get("status") != "downloaded":
            continue
        page = scan_page(Path(item["page_dir"]))
        page.update(position=item.get("position"), row=item.get("row"))
        pages.append(page)
        counts["pages"] += 1
        if page["status"] != "no_qr":
            counts["qr_pages"] += 1
        if page["status"] == "audio_downloaded":
            counts["audio_pages"] += 1
        elif page["status"] == "qr_unresolved":
            counts["unresolved_pages"] += 1
        print(
            f"[{counts['pages']}] QR/audio: {page['status']} - {page['source_page']}",
            flush=True,
        )
    output = {"counts": counts, "pages": pages}
    (run_dir / "qr_audio_manifest.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Decode worksheet QR codes and download public listening audio."
    )
    parser.add_argument("--run-dir", help="Run directory containing manifest.json")
    parser.add_argument("--source-page", help="Scan one source_page.jpg")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if bool(args.run_dir) == bool(args.source_page):
        raise SystemExit("Provide exactly one of --run-dir or --source-page")
    if args.source_page:
        result = scan_page(Path(args.source_page).resolve().parent)
    else:
        result = scan_run(Path(args.run_dir).resolve())
    print(json.dumps(result.get("counts", result), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
