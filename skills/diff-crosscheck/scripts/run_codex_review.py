# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""以唯讀 sandbox 執行 Codex CLI，依 reviewer brief 複核報告草稿。

brief 內容經 stdin 傳給 `codex exec --sandbox read-only`。Codex 的最終回覆寫到私有輸出目錄
（未指定 --out-dir 時由腳本以 mkdtemp 建立，避免另一個 reviewer 在完成前讀到），
並在 stdout 輸出執行狀態 JSON。status 為 completed 以外的值時以非零 exit code 結束。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

EXIT_FAILED = 1
EXIT_UNAVAILABLE = 3
REQUIRED_FLAGS = ["--sandbox", "--output-last-message"]


def tail(text: str, lines: int = 20) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])


def supported_flags(codex: str) -> str:
    result = subprocess.run([codex, "exec", "--help"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.stdout + result.stderr


def terminate(process: subprocess.Popen) -> None:
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="以唯讀 sandbox 執行 Codex CLI 複核報告草稿。")
    parser.add_argument("--repo", required=True, help="受審 repo 路徑，作為 Codex 的工作根目錄")
    parser.add_argument("--brief", required=True, help="reviewer brief 檔案路徑")
    parser.add_argument("--out-dir", help="輸出目錄；未指定時建立私有暫存目錄")
    parser.add_argument("--timeout", type=int, default=1800, help="逾時秒數（預設 1800）")
    parser.add_argument("--model", help="指定 Codex 模型；未指定時使用 Codex 設定的預設值")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    brief = Path(args.brief).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else Path(tempfile.mkdtemp(prefix="codex-review-"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "codex.md"
    partial = out_dir / ".codex.md.partial"
    log_path = out_dir / "codex.log"

    status = {
        "reviewer": "codex-cli",
        "status": "unavailable",
        "exit_code": None,
        "elapsed_seconds": 0,
        "output": str(out),
        "log": str(log_path),
        "stderr_tail": "",
        "command": "",
    }

    def finish(code: int) -> int:
        (out_dir / "codex.status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return code

    codex = shutil.which("codex")
    if codex is None:
        status["stderr_tail"] = "找不到 codex 指令；請安裝 Codex CLI 並完成登入後重試。"
        return finish(EXIT_UNAVAILABLE)
    if not brief.is_file():
        status.update(status="failed", stderr_tail=f"找不到 reviewer brief：{brief}")
        return finish(EXIT_FAILED)
    if not repo.is_dir():
        status.update(status="failed", stderr_tail=f"找不到受審 repo：{repo}")
        return finish(EXIT_FAILED)

    help_text = supported_flags(codex)
    missing = [flag for flag in REQUIRED_FLAGS if flag not in help_text]
    if missing:
        status.update(status="unavailable", stderr_tail=f"此版本的 codex exec 不支援必要旗標：{', '.join(missing)}；請更新 Codex CLI。")
        return finish(EXIT_UNAVAILABLE)

    command = [codex, "exec", "--sandbox", "read-only", "--output-last-message", str(partial)]
    if "--cd" in help_text:
        command += ["--cd", str(repo)]
    if "--ephemeral" in help_text:
        command.append("--ephemeral")
    if "--color" in help_text:
        command += ["--color", "never"]
    if args.model:
        command += ["--model", args.model]
    command.append("-")
    status["command"] = " ".join(command)

    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=str(repo),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        start_new_session=(os.name == "posix"),
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name != "posix" else 0,
    )
    try:
        stdout, stderr = process.communicate(input=brief.read_text(encoding="utf-8"), timeout=args.timeout)
    except subprocess.TimeoutExpired:
        terminate(process)
        stdout, stderr = process.communicate()
        log_path.write_text(f"{stdout}\n--- stderr ---\n{stderr}", encoding="utf-8")
        partial.unlink(missing_ok=True)
        status.update(
            status="timeout",
            elapsed_seconds=round(time.monotonic() - started),
            stderr_tail=f"超過 {args.timeout} 秒未完成，已終止 Codex。\n{tail(stderr)}",
        )
        return finish(EXIT_FAILED)

    log_path.write_text(f"{stdout}\n--- stderr ---\n{stderr}", encoding="utf-8")
    has_output = partial.is_file() and partial.read_text(encoding="utf-8", errors="replace").strip() != ""
    if has_output:
        partial.replace(out)
    if process.returncode == 0 and has_output:
        state = "completed"
    elif process.returncode == 0:
        state = "empty_output"
    else:
        state = "failed"
    status.update(
        status=state,
        exit_code=process.returncode,
        elapsed_seconds=round(time.monotonic() - started),
        stderr_tail=tail(stderr),
    )
    return finish(0 if state == "completed" else EXIT_FAILED)


if __name__ == "__main__":
    sys.exit(main())
