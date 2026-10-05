# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""記錄並比對受審 repo 的工作目錄快照，用來確認 reviewer 沒有修改任何檔案。

--save <file>：記錄 HEAD、分支、工作目錄與 staged 的 diff 雜湊、所有 ref，以及每個未追蹤檔案的內容雜湊。
--compare <file>：重新計算後比對，輸出差異；有差異時以 exit code 1 結束。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "--no-optional-locks", "-c", "core.quotepath=false", "-C", str(repo), *args],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失敗：{result.stderr.decode('utf-8', 'replace').strip()}")
    return result.stdout


def take_snapshot(repo: Path) -> dict:
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    branch = subprocess.run(
        ["git", "-C", str(repo), "symbolic-ref", "--quiet", "--short", "HEAD"], capture_output=True, text=True
    ).stdout.strip() or None
    tracked = git(repo, "diff", "--binary", "--no-color", "--no-ext-diff", "HEAD")
    staged = git(repo, "diff", "--cached", "--binary", "--no-color", "--no-ext-diff")
    refs = git(repo, "for-each-ref", "--format=%(refname) %(objectname)")
    untracked = {}
    for rel in git(repo, "ls-files", "--others", "--exclude-standard", "-z").decode("utf-8", "replace").split("\0"):
        if rel:
            path = repo / rel
            untracked[rel] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "not-a-file"
    return {
        "head": head,
        "branch": branch,
        "tracked_diff_sha256": hashlib.sha256(tracked).hexdigest(),
        "staged_diff_sha256": hashlib.sha256(staged).hexdigest(),
        "refs_sha256": hashlib.sha256(refs).hexdigest(),
        "untracked": untracked,
    }


def compare(before: dict, after: dict) -> list[str]:
    changes = []
    if before["head"] != after["head"]:
        changes.append(f"HEAD 由 {before['head'][:12]} 變為 {after['head'][:12]}")
    if before["branch"] != after["branch"]:
        changes.append(f"分支由 {before['branch']} 變為 {after['branch']}")
    if before["tracked_diff_sha256"] != after["tracked_diff_sha256"]:
        changes.append("已追蹤檔案的內容有變動")
    if "staged_diff_sha256" in before and before["staged_diff_sha256"] != after["staged_diff_sha256"]:
        changes.append("staged 狀態有變動")
    if "refs_sha256" in before and before["refs_sha256"] != after["refs_sha256"]:
        changes.append("分支、tag 或 stash 等 ref 有變動")
    added = sorted(set(after["untracked"]) - set(before["untracked"]))
    removed = sorted(set(before["untracked"]) - set(after["untracked"]))
    modified = sorted(p for p in set(before["untracked"]) & set(after["untracked"]) if before["untracked"][p] != after["untracked"][p])
    if added:
        changes.append(f"新增未追蹤檔案：{added[:20]}")
    if removed:
        changes.append(f"未追蹤檔案被刪除：{removed[:20]}")
    if modified:
        changes.append(f"未追蹤檔案內容改變：{modified[:20]}")
    return changes


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="記錄或比對受審 repo 的工作目錄快照。")
    parser.add_argument("--repo", required=True, help="受審 repo 路徑")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--save", help="把目前快照寫入此檔案")
    action.add_argument("--compare", help="與此快照檔比對")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    try:
        current = take_snapshot(repo)
    except (RuntimeError, OSError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2

    if args.save:
        Path(args.save).parent.mkdir(parents=True, exist_ok=True)
        Path(args.save).write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"ok": True, "saved": args.save, "head": current["head"]}, ensure_ascii=False))
        return 0

    try:
        before = json.loads(Path(args.compare).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": f"無法讀取快照檔：{error}"}, ensure_ascii=False))
        return 2
    changes = compare(before, current)
    print(json.dumps({"ok": True, "unchanged": not changes, "changes": changes}, ensure_ascii=False, indent=2))
    return 0 if not changes else 1


if __name__ == "__main__":
    sys.exit(main())
