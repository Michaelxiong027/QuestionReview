from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = "config.cloud.json"


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(
            f"Config not found: {path}\n"
            f"Copy config.cloud.example.json to {DEFAULT_CONFIG} and edit it first."
        )
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def latest_xlsx(root: Path) -> Path:
    candidates = [
        p for p in root.glob("*.xlsx")
        if not p.name.startswith("~$") and p.is_file()
    ]
    if not candidates:
        raise SystemExit("No .xlsx file found in current directory.")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def render_template(value: str, file_path: Path, remote_name: str) -> str:
    return value.format(
        file=str(file_path),
        file_ps=str(file_path).replace("'", "''"),
        filename=file_path.name,
        stem=file_path.stem,
        remote_name=remote_name,
    )


def run_custom_command(config: dict[str, Any], file_path: Path, dry_run: bool) -> str:
    command_config = config.get("custom_command") or {}
    command = command_config.get("command")
    if not command:
        raise SystemExit("custom_command.command is required when provider=custom_command.")

    remote_name = str(command_config.get("remote_name") or file_path.name)
    rendered = render_template(str(command), file_path, remote_name)
    shell = bool(command_config.get("shell", True))
    timeout = int(command_config.get("timeout_seconds") or 1800)

    print(f"[cloud] provider=custom_command")
    print(f"[cloud] file={file_path}")
    print(f"[cloud] command={rendered}")
    if dry_run:
        return ""

    completed = subprocess.run(
        rendered if shell else rendered.split(),
        shell=shell,
        cwd=str(file_path.parent),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    output = completed.stdout or ""
    print(output.rstrip())
    if completed.returncode != 0:
        raise SystemExit(f"Upload command failed with exit code {completed.returncode}.")

    regex = command_config.get("link_regex") or r"https?://[^\s\"'<>]+"
    match = re.search(str(regex), output)
    if not match:
        raise SystemExit(
            "Upload command finished, but no download link was found in output. "
            "Adjust custom_command.link_regex in config.cloud.json."
        )
    return match.group(1)


def copy_to_sync_folder(config: dict[str, Any], file_path: Path, dry_run: bool) -> str:
    sync_config = config.get("baidu_sync_folder") or {}
    folder = sync_config.get("folder")
    if not folder:
        raise SystemExit("baidu_sync_folder.folder is required when provider=baidu_sync_folder.")

    target_dir = Path(os.path.expandvars(str(folder))).expanduser()
    target = target_dir / file_path.name
    print(f"[cloud] provider=baidu_sync_folder")
    print(f"[cloud] file={file_path}")
    print(f"[cloud] target={target}")
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, target)

    return (
        "已复制到百度网盘同步目录。等待客户端同步完成后，"
        "请在百度网盘客户端或网页中右键该文件生成分享链接。"
    )


def write_result(path: Path, file_path: Path, result: str) -> None:
    payload = {
        "file": str(file_path),
        "result": result,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload a deliverable file and print a cloud download link.")
    parser.add_argument("--file", help="File to upload. Defaults to latest .xlsx in current directory.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help=f"Config path. Default: {DEFAULT_CONFIG}")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without uploading.")
    parser.add_argument("--result", default="cloud_upload_result.json", help="Result JSON path.")
    args = parser.parse_args()

    root = Path.cwd()
    file_path = Path(args.file).expanduser() if args.file else latest_xlsx(root)
    if not file_path.is_absolute():
        file_path = root / file_path
    file_path = file_path.resolve()
    if not file_path.exists() or not file_path.is_file():
        raise SystemExit(f"File not found: {file_path}")

    config = load_config((root / args.config).resolve() if not Path(args.config).is_absolute() else Path(args.config))
    provider = str(config.get("provider") or "disabled").strip().lower()

    if provider == "custom_command":
        result = run_custom_command(config, file_path, args.dry_run)
    elif provider == "baidu_sync_folder":
        result = copy_to_sync_folder(config, file_path, args.dry_run)
    else:
        raise SystemExit(
            "Cloud upload is disabled. Set provider to custom_command or baidu_sync_folder "
            "in config.cloud.json."
        )

    if result:
        print(f"[cloud] result={result}")
        write_result((root / args.result).resolve(), file_path, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



