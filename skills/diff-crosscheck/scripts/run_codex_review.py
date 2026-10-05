# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""以唯讀 sandbox 執行 Codex CLI 複核報告草稿，並依錯誤類型決定是否自動重試。

brief 內容經 stdin 傳給 `codex exec --json --sandbox read-only`。Codex 的最終回覆寫到私有輸出目錄
（未指定 --out-dir 時由腳本以 mkdtemp 建立，避免另一個 reviewer 在完成前讀到），
並在 stdout 輸出執行狀態 JSON，同時寫入輸出目錄的 codex.status.json。

錯誤類型優先取自 Codex session 紀錄的 `codex_error_info`，找不到時才比對 `--json` 錯誤事件的訊息：
- capacity（模型過載）：等待後以 `codex exec resume` 接續同一個 session 重試一次，再依序改用
  --fallback-model 或環境變數 DIFF_REVIEW_CODEX_FALLBACK_MODELS（以逗號分隔）指定的模型接續；
  仍失敗時回報 capacity，並在 model_candidates 列出 Codex 模型目錄中尚未嘗試的模型。
- transient（連線中斷、伺服器錯誤、速率限制）：等待後接續同一個 session 重試。
- 其他錯誤（未登入、用量上限、context 超限等）：不重試，直接回報原因（reason）與建議（action）。
接續前會從 session 紀錄確認每一輪的 sandbox 皆為 read-only；找不到紀錄時不接續，改為從頭執行。
--timeout 是含重試與等待的整體時間上限。使用者選定模型後，以 --resume <session_id> --model <模型>
接續先前的 session；搭配同一個 --out-dir 時，沿用先前的嘗試紀錄。
status 為 completed 以外的值時以非零 exit code 結束。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

EXIT_FAILED = 1
EXIT_UNAVAILABLE = 3
REQUIRED_FLAGS = ["--sandbox", "--output-last-message", "--json", "resume"]
CAPACITY_WAITS = [30]
FALLBACK_WAIT = 5
TRANSIENT_WAITS = [30, 90]
MIN_ATTEMPT_SECONDS = 60
RESUME_PROMPT = "先前的執行因錯誤中斷。請接續完成原本的複核，維持唯讀限制，並依原指示的回覆格式輸出完整結果。"

ERROR_CODES = {
    "server_overloaded": "capacity",
    "http_connection_failed": "transient",
    "response_stream_connection_failed": "transient",
    "response_stream_disconnected": "transient",
    "internal_server_error": "transient",
    "rate_limit_exceeded": "transient",
    "unauthorized": "auth",
    "usage_limit_exceeded": "usage_limit",
    "context_window_exceeded": "context_limit",
}
# 只用來比對錯誤事件的訊息；Codex 的執行紀錄含受審程式碼，不可拿來比對。
ERROR_PATTERNS = [
    ("capacity", re.compile(r"at capacity|overloaded", re.IGNORECASE)),
    ("usage_limit", re.compile(r"usage limit|quota", re.IGNORECASE)),
    ("context_limit", re.compile(r"context window|context length", re.IGNORECASE)),
    ("auth", re.compile(r"unauthori[sz]ed|\b401\b|auth|log ?in", re.IGNORECASE)),
    ("transient", re.compile(r"disconnected|connection|timed? ?out|rate limit|\b429\b|\b5\d\d\b", re.IGNORECASE)),
]
OUTCOMES = {
    "completed": ("Codex 已完成複核。", ""),
    "capacity": (
        "模型容量不足，等待、接續與備援模型都無法完成。",
        "請使用者從 model_candidates 選擇模型後，加上 --resume {session} --model <模型> 接續；"
        "也可設定 DIFF_REVIEW_CODEX_FALLBACK_MODELS，讓之後自動改用備援模型。",
    ),
    "transient": ("連線中斷或伺服器暫時錯誤，重試後仍失敗。", "確認網路後，加上 --resume {session} 接續。"),
    "auth": ("Codex 未登入或登入已失效。", "執行 `codex login` 後重跑。"),
    "usage_limit": ("已達 Codex 用量上限。", "等待用量重置，或改用其他帳號或方案後重跑。"),
    "context_limit": ("複核內容超過模型的 context 上限。", "縮小 diff 範圍或拆成多次複核後重跑。"),
    "timeout": ("超過整體時間上限仍未完成，已終止 Codex。", "加上 --resume {session} 接續，或以 --timeout 放寬上限後重跑。"),
    "unsafe_sandbox": (
        "Codex 的實際 sandbox 不是 read-only，結果不可採用。",
        "確認受審 repo 未被修改，檢查 ~/.codex/config.toml 與 Codex CLI 版本後重跑。",
    ),
    "empty_output": ("Codex 結束但沒有輸出最終回覆。", "檢查 codex.log 後重跑。"),
    "failed": ("Codex 執行失敗。", "依 message 與 codex.log 排除問題後重跑。"),
}


def tail(text: str, lines: int = 20) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])


def terminate(process: subprocess.Popen) -> None:
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)


def run_attempt(command: list[str], stdin_text: str, cwd: Path, timeout: float) -> dict:
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        start_new_session=(os.name == "posix"),
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name != "posix" else 0,
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(input=stdin_text, timeout=timeout)
    except subprocess.TimeoutExpired:
        terminate(process)
        stdout, stderr = process.communicate()
        timed_out = True
    return {
        "exit_code": process.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": timed_out,
        "elapsed": round(time.monotonic() - started),
    }


def readable(message: str) -> str:
    """錯誤事件的訊息常是 API 回應的 JSON 字串，取出其中的說明文字。"""
    try:
        data = json.loads(message)
        return str(data.get("error", {}).get("message") or message)
    except (ValueError, AttributeError):
        return message


def parse_events(stdout: str) -> tuple[str | None, list[str]]:
    thread_id, messages = None, []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
        elif event.get("type") == "error":
            messages.append(readable(str(event.get("message", ""))))
        elif event.get("type") == "turn.failed":
            messages.append(readable(str((event.get("error") or {}).get("message", ""))))
    return thread_id, messages


def find_rollout(session_id: str) -> Path | None:
    home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    matches = sorted(home.glob(f"sessions/*/*/*/rollout-*{session_id}.jsonl"))
    return matches[-1] if matches else None


def rollout_lines(rollout: Path | None) -> list[str]:
    if rollout is None or not rollout.is_file():
        return []
    return rollout.read_text(encoding="utf-8", errors="replace").splitlines()


def summarize_turns(lines: list[str]) -> dict:
    """從 session 紀錄取出每一輪的模型、sandbox，以及最後一輪的錯誤碼。"""
    summary = {"models": [], "sandboxes": [], "code": None}
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        payload = event.get("payload") if isinstance(event, dict) else None
        if not isinstance(payload, dict):
            continue
        if event.get("type") == "turn_context":
            summary["models"].append(payload.get("model"))
            summary["sandboxes"].append((payload.get("sandbox_policy") or {}).get("type"))
        elif payload.get("type") == "task_complete":
            info = (payload.get("error") or {}).get("codex_error_info")
            summary["code"] = next(iter(info), None) if isinstance(info, dict) else info
    return summary


def classify(result: dict, code: str | None, messages: list[str]) -> str:
    if result["timed_out"]:
        return "timeout"
    if result["exit_code"] == 0:
        return "ok"
    if code in ERROR_CODES:
        return ERROR_CODES[code]
    if code and code != "other":
        return "failed"
    text = "\n".join(messages)
    for kind, pattern in ERROR_PATTERNS:
        if pattern.search(text):
            return kind
    return "failed"


def model_candidates(codex: str, tried: set) -> list[dict]:
    try:
        result = subprocess.run(
            [codex, "debug", "models"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60
        )
        models = json.loads(result.stdout).get("models", [])
    except (OSError, subprocess.SubprocessError, ValueError, AttributeError):
        return []
    listed = [m for m in models if isinstance(m, dict) and m.get("visibility") == "list" and m.get("slug") not in tried]
    listed.sort(key=lambda m: m.get("priority", 999))
    return [{"model": m["slug"], "name": m.get("display_name", m["slug"])} for m in listed]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="以唯讀 sandbox 執行 Codex CLI 複核報告草稿。")
    parser.add_argument("--repo", required=True, help="受審 repo 路徑，作為 Codex 的工作根目錄")
    parser.add_argument("--brief", required=True, help="reviewer brief 檔案路徑")
    parser.add_argument("--out-dir", help="輸出目錄；未指定時建立私有暫存目錄")
    parser.add_argument("--timeout", type=int, default=2400, help="含重試與等待的整體時間上限秒數（預設 2400）")
    parser.add_argument("--model", help="指定 Codex 模型；未指定時使用 Codex 設定的預設值")
    parser.add_argument("--fallback-model", action="append", default=[],
                        help="容量不足且同一模型重試仍失敗時依序改用的模型，可重複指定")
    parser.add_argument("--resume", metavar="SESSION_ID", help="接續先前因錯誤中斷的 session")
    args = parser.parse_args()

    fallbacks = args.fallback_model or [
        m.strip() for m in os.environ.get("DIFF_REVIEW_CODEX_FALLBACK_MODELS", "").split(",") if m.strip()
    ]
    fallbacks = [m for i, m in enumerate(fallbacks) if m != args.model and m not in fallbacks[:i]]
    repo = Path(args.repo).expanduser().resolve()
    brief = Path(args.brief).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else Path(tempfile.mkdtemp(prefix="codex-review-"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "codex.md"
    partial = out_dir / ".codex.md.partial"
    log_path = out_dir / "codex.log"
    status_path = out_dir / "codex.status.json"

    previous = []
    if args.resume and status_path.is_file():
        try:
            previous = json.loads(status_path.read_text(encoding="utf-8")).get("attempts", [])
        except (ValueError, AttributeError):
            previous = []
    status = {
        "reviewer": "codex-cli",
        "status": "unavailable",
        "reason": "",
        "action": "",
        "message": "",
        "exit_code": None,
        "elapsed_seconds": 0,
        "model_used": None,
        "session_id": args.resume,
        "sandbox_verified": False,
        "attempts": previous,
        "model_candidates": [],
        "out_dir": str(out_dir),
        "output": str(out),
        "log": str(log_path),
    }

    def finish(code: int) -> int:
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return code

    codex = shutil.which("codex")
    if codex is None:
        status.update(reason="找不到 codex 指令。", action="安裝 Codex CLI 並執行 `codex login` 後重跑。")
        return finish(EXIT_UNAVAILABLE)
    if not brief.is_file():
        status.update(status="failed", reason=f"找不到 reviewer brief：{brief}")
        return finish(EXIT_FAILED)
    if not repo.is_dir():
        status.update(status="failed", reason=f"找不到受審 repo：{repo}")
        return finish(EXIT_FAILED)

    exec_help = subprocess.run([codex, "exec", "--help"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    help_text = exec_help.stdout + exec_help.stderr
    missing = [flag for flag in REQUIRED_FLAGS if flag not in help_text]
    if missing:
        status.update(reason=f"此版本的 codex exec 不支援：{', '.join(missing)}。", action="更新 Codex CLI 後重跑。")
        return finish(EXIT_UNAVAILABLE)

    session_id = args.resume
    rollout = find_rollout(session_id) if session_id else None
    if session_id and rollout is None:
        status.update(
            status="failed",
            reason=f"找不到 session {session_id} 的紀錄，無法確認 sandbox，不接續。",
            action="不帶 --resume 從頭執行。",
        )
        return finish(EXIT_FAILED)

    def exec_command(model: str | None) -> list[str]:
        command = [codex, "exec", "--json", "--sandbox", "read-only", "--output-last-message", str(partial)]
        if "--cd" in help_text:
            command += ["--cd", str(repo)]
        if model:
            command += ["--model", model]
        return command + ["-"]

    def resume_command(model: str | None) -> list[str]:
        command = [codex, "exec", "resume", session_id, "--json", "-c", 'sandbox_mode="read-only"',
                   "--output-last-message", str(partial)]
        if model:
            command += ["--model", model]
        return command + ["-"]

    brief_text = brief.read_text(encoding="utf-8")
    capacity_plan = [(args.model, wait) for wait in CAPACITY_WAITS] + [(m, FALLBACK_WAIT) for m in fallbacks]
    transient_plan = [(None, wait) for wait in TRANSIENT_WAITS]
    model = args.model
    started = time.monotonic()
    deadline = started + args.timeout
    out_of_time = False
    observed = []

    while True:
        resuming = rollout is not None
        offset = len(rollout_lines(rollout))
        partial.unlink(missing_ok=True)
        result = run_attempt(
            resume_command(model) if resuming else exec_command(model),
            RESUME_PROMPT if resuming else brief_text,
            repo,
            max(deadline - time.monotonic(), 1),
        )
        thread_id, messages = parse_events(result["stdout"])
        if not messages and result["exit_code"] != 0:
            messages = [tail(result["stderr"])]
        if thread_id and not resuming:
            session_id = thread_id
            rollout = find_rollout(session_id)
        turns = summarize_turns(rollout_lines(rollout)[offset:])
        unsafe = any(sandbox != "read-only" for sandbox in turns["sandboxes"])
        observed += turns["sandboxes"]
        outcome = "unsafe_sandbox" if unsafe else classify(result, turns["code"], messages)
        status["attempts"].append({
            "kind": "resume" if resuming else "exec",
            "model": turns["models"][-1] if turns["models"] else model,
            "elapsed_seconds": result["elapsed"],
            "result": outcome,
            "error_code": turns["code"],
            "message": messages[-1][:500] if messages else "",
        })
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"===== attempt {len(status['attempts'])}（{status['attempts'][-1]['kind']}）=====\n"
                      f"{result['stdout']}\n--- stderr ---\n{result['stderr']}\n\n")
        plan = {"capacity": capacity_plan, "transient": transient_plan}.get(outcome)
        if not plan:
            break
        next_model, wait = plan.pop(0)
        if deadline - time.monotonic() - wait < MIN_ATTEMPT_SECONDS:
            out_of_time = True
            break
        time.sleep(wait)
        if outcome == "capacity":
            model = next_model

    has_output = partial.is_file() and partial.read_text(encoding="utf-8", errors="replace").strip() != ""
    if outcome == "ok":
        state = "completed" if has_output else "empty_output"
    else:
        state = outcome
    if state == "completed":
        partial.replace(out)
    else:
        partial.unlink(missing_ok=True)
    reason, action = OUTCOMES[state]
    if out_of_time:
        reason += "（剩餘時間不足，未再重試）"
    if state == "capacity":
        tried = {attempt.get("model") for attempt in status["attempts"]}
        status["model_candidates"] = model_candidates(codex, tried)
    status.update(
        status=state,
        reason=reason,
        action=action.format(session=session_id or "<session_id>"),
        message=status["attempts"][-1]["message"],
        exit_code=result["exit_code"],
        elapsed_seconds=round(time.monotonic() - started),
        model_used=status["attempts"][-1]["model"],
        session_id=session_id,
        sandbox_verified=bool(observed) and all(sandbox == "read-only" for sandbox in observed),
    )
    return finish(0 if state == "completed" else EXIT_FAILED)


if __name__ == "__main__":
    sys.exit(main())
