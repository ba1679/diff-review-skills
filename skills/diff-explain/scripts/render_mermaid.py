# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""以無頭 Chrome / Chromium 渲染 Markdown 報告中的 Mermaid 圖，檢查語法錯誤與文字重疊，並逐張截圖。

依序取出報告中的 ```mermaid 區塊，產生載入 Mermaid 11（預設取自 jsDelivr CDN）的檢查頁，
先以 --dump-dom 取得每張圖的渲染結果、節點數與互相重疊的節點／標籤，再逐張以 --screenshot 截圖。
stdout 輸出結果 JSON；截圖供檢視自動偵測不到的問題（例如連線穿過節點、版面過擠）。

exit code：0＝每張圖都能渲染且未偵測到重疊；1＝有語法錯誤或重疊；2＝輸入錯誤；
3＝找不到瀏覽器或無法載入 Mermaid（例如離線），圖未經驗證。
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXIT_PROBLEMS = 1
EXIT_INPUT = 2
EXIT_UNAVAILABLE = 3
DEFAULT_MERMAID_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"
VIEW_WIDTH = 1400
FENCE_OPEN = re.compile(r"^```mermaid\s*$")
FENCE_CLOSE = re.compile(r"^```\s*$")
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")
RESULT = re.compile(r'<pre id="result">(.*?)</pre>', re.DOTALL)
PLAYWRIGHT_BINARIES = ["chrome-headless-shell", "chrome-headless-shell.exe", "headless_shell", "headless_shell.exe"]
BROWSER_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
BROWSER_COMMANDS = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge"]

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>mermaid check</title>
<style>
body { margin: 0; background: #fff; font-family: -apple-system, "Segoe UI", "Noto Sans TC", sans-serif; }
section { padding: 12px 20px; }
h2 { font-size: 14px; margin: 0 0 8px; color: #334155; }
body.shot #result { display: none; }
</style></head>
<body>
<div id="diagrams"></div>
<pre id="result">pending</pre>
<script id="sources" type="application/json">__SOURCES__</script>
<script type="module">
const resultEl = document.getElementById('result');
const sources = JSON.parse(document.getElementById('sources').textContent);
const only = location.hash ? Number(location.hash.slice(1)) : null;
if (only !== null) document.body.classList.add('shot');
let mermaid;
try {
  mermaid = (await import(__MERMAID_URL__)).default;
} catch (error) {
  resultEl.textContent = JSON.stringify({ loaded: false, error: String(error && error.message || error) });
  throw error;
}
mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'default' });

function inspect(svg) {
  const boxes = [];
  const add = (el, kind) => {
    const text = (el.textContent || '').replace(/\\s+/g, ' ').trim();
    const r = el.getBoundingClientRect();
    if (text && r.width >= 1 && r.height >= 1) boxes.push({ el, kind, text: text.slice(0, 30), r });
  };
  svg.querySelectorAll('g.node').forEach((el) => add(el, '節點'));
  svg.querySelectorAll('g.edgeLabel').forEach((el) => add(el, '連線標籤'));
  svg.querySelectorAll('g.cluster-label').forEach((el) => add(el, '群組標題'));
  svg.querySelectorAll('text.messageText, text.noteText, text.loopText').forEach((el) => add(el, '文字'));
  const overlaps = [];
  for (let a = 0; a < boxes.length; a += 1) {
    for (let b = a + 1; b < boxes.length; b += 1) {
      const A = boxes[a];
      const B = boxes[b];
      if (A.el.contains(B.el) || B.el.contains(A.el)) continue;
      const w = Math.min(A.r.right, B.r.right) - Math.max(A.r.left, B.r.left);
      const h = Math.min(A.r.bottom, B.r.bottom) - Math.max(A.r.top, B.r.top);
      if (w > 2 && h > 2) overlaps.push(`${A.kind}「${A.text}」與${B.kind}「${B.text}」`);
    }
  }
  return { nodes: svg.querySelectorAll('g.node').length, overlaps };
}

const report = [];
for (const [i, item] of sources.entries()) {
  if (only !== null && i !== only) continue;
  const section = document.createElement('section');
  section.innerHTML = '<h2></h2><div class="out"></div>';
  section.querySelector('h2').textContent = `#${i + 1} ${item.label}`;
  document.getElementById('diagrams').append(section);
  const entry = { index: i + 1, label: item.label, line: item.line, ok: false };
  try {
    const { svg } = await mermaid.render(`m${i}`, item.source);
    section.querySelector('.out').innerHTML = svg;
    entry.ok = true;
    Object.assign(entry, inspect(section.querySelector('svg')));
  } catch (error) {
    entry.error = String(error && error.message || error).split('\\n').slice(0, 4).join(' ');
    document.getElementById(`dm${i}`)?.remove();
  }
  entry.height = Math.ceil(section.getBoundingClientRect().height);
  report.push(entry);
}
resultEl.textContent = JSON.stringify({ loaded: true, diagrams: report });
</script>
</body></html>
"""


def extract_diagrams(text: str) -> list[dict]:
    diagrams, label, block, start = [], "", None, 0
    for number, line in enumerate(text.splitlines(), start=1):
        if block is None:
            heading = HEADING.match(line)
            if heading:
                label = heading.group(1)
            elif FENCE_OPEN.match(line):
                block, start = [], number
        elif FENCE_CLOSE.match(line):
            diagrams.append({"label": label or "（無標題）", "line": start, "source": "\n".join(block)})
            block = None
        else:
            block.append(line)
    return diagrams


def find_browser(explicit: str | None) -> str | None:
    candidates = [c for c in (explicit, os.environ.get("DIFF_REVIEW_BROWSER")) if c]
    roots = [Path.home() / "Library/Caches/ms-playwright", Path.home() / ".cache/ms-playwright"]
    if os.environ.get("LOCALAPPDATA"):
        roots.append(Path(os.environ["LOCALAPPDATA"]) / "ms-playwright")
    for root in roots:
        for name in PLAYWRIGHT_BINARIES:
            candidates += [str(p) for p in sorted(root.glob(f"chromium_headless_shell-*/*/{name}"), reverse=True)]
    candidates += BROWSER_PATHS
    candidates += [found for found in map(shutil.which, BROWSER_COMMANDS) if found]
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    return None


def run_browser(browser: str, profile: Path, args: list[str], timeout: int) -> str | None:
    """執行瀏覽器並回傳 stdout；逾時或無法啟動時回傳 None。"""
    command = [browser, "--headless", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
               "--no-default-browser-check", "--disable-extensions", f"--user-data-dir={profile}",
               "--virtual-time-budget=20000", *args]
    try:
        return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout).stdout
    except (subprocess.TimeoutExpired, OSError):
        return None


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="渲染 Markdown 報告中的 Mermaid 圖，檢查語法錯誤與文字重疊並截圖。")
    parser.add_argument("--report", required=True, help="含 ```mermaid 區塊的 Markdown 檔")
    parser.add_argument("--out-dir", help="檢查頁與截圖的輸出目錄（預設：報告所在目錄的 mermaid-check/）")
    parser.add_argument("--browser", help="Chrome / Chromium 執行檔；未指定時依序找 DIFF_REVIEW_BROWSER、Playwright 與常見安裝位置")
    parser.add_argument("--mermaid-url", default=DEFAULT_MERMAID_URL, help="Mermaid ESM 模組網址（離線時可指向本機檔案）")
    parser.add_argument("--max-nodes", type=int, default=11, help="單張圖的建議節點上限，超過時列為提醒（預設 11）")
    parser.add_argument("--timeout", type=int, default=90, help="每次啟動瀏覽器的時間上限秒數（預設 90）")
    args = parser.parse_args()

    report = Path(args.report).expanduser().resolve()
    if not report.is_file():
        print(json.dumps({"ok": False, "status": "input_error", "message": f"找不到報告：{report}"}, ensure_ascii=False))
        return EXIT_INPUT
    diagrams = extract_diagrams(report.read_text(encoding="utf-8"))
    result = {"ok": True, "status": "ok", "report": str(report), "browser": None, "html": None,
              "message": "", "diagrams": []}
    if not diagrams:
        result["message"] = "報告中沒有 Mermaid 圖。"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    browser = find_browser(args.browser)
    if browser is None:
        result.update(ok=False, status="unavailable",
                      message="找不到 Chrome / Chromium；以 --browser 或 DIFF_REVIEW_BROWSER 指定執行檔後重跑。")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return EXIT_UNAVAILABLE

    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else report.parent / "mermaid-check"
    out_dir.mkdir(parents=True, exist_ok=True)
    page = out_dir / f"{report.stem}-mermaid.html"
    sources = json.dumps([{k: d[k] for k in ("label", "line", "source")} for d in diagrams], ensure_ascii=False)
    page.write_text(PAGE.replace("__SOURCES__", sources.replace("</", "<\\/"))
                    .replace("__MERMAID_URL__", json.dumps(args.mermaid_url)), encoding="utf-8")
    result.update(browser=browser, html=str(page))

    with tempfile.TemporaryDirectory(prefix="mermaid-check-") as profile:
        dumped = run_browser(browser, Path(profile), [f"--window-size={VIEW_WIDTH},1000", "--dump-dom",
                                                      page.as_uri()], args.timeout)
        match = RESULT.search(dumped) if dumped else None
        try:
            payload = json.loads(html.unescape(match.group(1))) if match else {}
        except ValueError:
            payload = {}
        if not payload.get("loaded"):
            reason = payload.get("error") or "瀏覽器無法啟動、逾時或未回傳結果"
            result.update(ok=False, status="unavailable", message=f"無法載入 Mermaid 或完成渲染：{reason}")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return EXIT_UNAVAILABLE

        for entry in payload["diagrams"]:
            entry["warnings"] = []
            if entry.get("nodes", 0) > args.max_nodes:
                entry["warnings"].append(f"節點 {entry['nodes']} 個，超過建議上限 {args.max_nodes}")
            if entry["ok"]:
                shot = out_dir / f"{report.stem}-mermaid-{entry['index']}.png"
                height = max(entry.get("height", 0), 200) + 20
                shot.unlink(missing_ok=True)
                run_browser(browser, Path(profile), [f"--screenshot={shot}", f"--window-size={VIEW_WIDTH},{height}",
                                                     f"{page.as_uri()}#{entry['index'] - 1}"], args.timeout)
                entry["screenshot"] = str(shot) if shot.is_file() else None
                if entry["screenshot"] is None:
                    entry["warnings"].append("截圖失敗，版面未經目視檢查")
            entry.pop("height", None)
            result["diagrams"].append(entry)

    failed = [d for d in result["diagrams"] if not d["ok"] or d.get("overlaps")]
    if failed:
        result.update(ok=False, status="problems",
                      message=f"{len(failed)} 張圖有語法錯誤或重疊，修正後重跑；截圖仍需檢視。")
    else:
        result["message"] = "全部圖都能渲染且未偵測到重疊；請檢視截圖確認沒有自動偵測不到的版面問題。"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return EXIT_PROBLEMS if failed else 0


if __name__ == "__main__":
    sys.exit(main())
