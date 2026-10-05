---
name: diff-explain
description: 協助開發者看懂一段 git diff：固定 base / head SHA 後，以程式碼證據說明改動要解決的問題、修改後行為、功能分組與必要性，並依資訊價值繪製 Mermaid 改動圖；只說明改動，不產出 review findings。使用者說「這個 PR 在做什麼」「幫我看懂這個 PR／這段 diff」「解釋這次改動」「A 和 B 差在哪」「A -> B 改了什麼」「畫改動圖」「what changed / explain this PR」，或被 diff-review 串接時使用。
---

# Diff 改動理解

固定比較範圍後，以程式碼證據說明改動並繪製改動圖；所有人類可讀輸出使用繁體中文。

文中的 `rules/`、`templates/`、`scripts/` 路徑皆相對於本 skill 目錄；腳本只用 Python 標準函式庫，預設以 `uv run` 執行，`uv` 不可用時改用 `python3`。

# SOP

## Phase 1 -- 固定比較範圍

1. READ 讀取使用者輸入與 `rules/scope-resolution.md`，依規則收斂受審 repo、PR URL、base / head、比較方式與是否納入未提交改動。
2. DELEGATE 依收斂結果執行 `uv run scripts/resolve_diff_scope.py --repo <受審 repo> [--pr <URL>] [--base <ref>] [--head <ref>] [--mode merge-base|direct] [--include-uncommitted] [--run-root <session 暫存目錄>]`，在受審 repo 之外建立執行目錄並固定 base / head / merge-base SHA，產出 `run.json`、`diff.patch` 與 `pr.md`；腳本以非零 exit code 結束時，依已載入規則轉述錯誤並停止。
3. WRITE 讀取 `templates/explain-report.md` 與 `templates/explain-report.example.md`，依骨架的「比較範圍」區塊、參考範例填入 `run.json` 的內容，依已載入規則向使用者顯示比較範圍並處理 `warnings`。

## Phase 2 -- 讀懂改動並收集證據

1. READ 讀取 `rules/evidence-and-reading-scope.md`，以 `diff.patch` 為入口，依規則按需閱讀相關程式碼並蒐集需求來源。
2. THINK 讀取 `rules/change-understanding-and-diagrams.md`，收斂本次要解決的問題與修改後行為、功能分組、各組目的與必要性，以及要繪製的圖。

## Phase 3 -- 產出改動說明

1. WRITE 依已讀取的改動說明樣板複製骨架結構、參考範例改寫填位符號與具體內容，在執行目錄產出改動說明草稿 `draft.md`，並把實際讀取的需求來源路徑寫入 `run.json` 的 `requirement_sources`。
2. WRITE 若由使用者直接呼叫，回傳改動說明，並告知可用 `/diff-crosscheck <執行目錄>` 交由獨立 reviewer 複核；若由 `diff-review` 串接，回傳執行目錄路徑。
