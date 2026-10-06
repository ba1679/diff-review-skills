---
name: diff-crosscheck
description: 對 diff-explain 或 diff-review 產出的執行目錄（含固定 base / head SHA 的 run.json 與報告草稿），平行交由一個獨立唯讀 subagent 與 Codex CLI 複核，再由主 agent 對照程式碼重新查證、統整成最終報告。由 diff-review 串接，或使用者提供執行目錄並要求「雙重複核」「第二意見」「用 Codex 複核」「cross-check 這份報告」時使用；沒有執行目錄時，先用 diff-explain 或 diff-review 建立。
---

# Diff 獨立雙重複核

讓兩個彼此隔離的 reviewer 以相同的固定範圍複核同一份草稿，再由主 agent 對照程式碼統整；所有人類可讀輸出使用繁體中文。

文中的 `rules/`、`templates/`、`scripts/` 路徑皆相對於本 skill 目錄；腳本只用 Python 標準函式庫，預設以 `uv run` 執行，`uv` 不可用時改用 `python3`。

# SOP

## Phase 1 -- 確認複核輸入

1. READ 讀取執行目錄的 `run.json` 與 `draft.md`，確認 repo、base / head SHA、比較方式、`report_kind`、`diff.patch` 與 `criteria` 齊備且 SHA 仍可解析（`mode` 為 `direct` 時 `merge_base` 可以為空）；缺漏時向使用者說明並停止。

## Phase 2 -- 完成獨立雙重複核

1. WRITE 讀取 `rules/reviewer-dispatch-and-independence.md`、`templates/reviewer-brief.md` 與 `templates/reviewer-brief.example.md`，依規則與骨架複製結構、參考範例以 `run.json` 與 `draft.md` 的內容改寫填位符號，在執行目錄產出兩個 reviewer 共用的 `reviewer-brief.md`。
2. DELEGATE 執行 `uv run scripts/check_worktree.py --repo <受審 repo> --save <reviews_dir>/worktree-before.json` 記錄工作目錄快照（`<reviews_dir>` 為 `run.json` 的 `artifacts.reviews_dir`），再依已載入規則平行啟動 subagent（交付 `reviewer-brief.md` 的路徑）與在背景執行 `uv run scripts/run_codex_review.py --repo <受審 repo> --brief <reviewer-brief.md>` 的 Codex 複核。
3. DELEGATE Codex 狀態 JSON 的 `status` 為 `capacity` 時，依已載入規則處理換模型；使用者指定模型後，在背景執行 `uv run scripts/run_codex_review.py --repo <受審 repo> --brief <reviewer-brief.md> --resume <session_id> --model <模型> --out-dir <out_dir>` 接續原 session。
4. READ 兩者都結束後，讀取 subagent 的回傳內容與 Codex 狀態 JSON 指向的輸出。
5. WRITE 把兩份結果存入 `<reviews_dir>`，並執行 `uv run scripts/check_worktree.py --repo <受審 repo> --compare <reviews_dir>/worktree-before.json` 確認 reviewer 沒有修改受審 repo；任一方失敗或工作目錄有變動時，依已載入規則記錄並揭露。

## Phase 3 -- 統整並產出最終報告

1. THINK 讀取 `rules/consolidation-criteria.md` 與 `run.json` 的 `criteria` 列出的規則，對照程式碼逐項重新查證兩份複核意見，收斂合併、排除、修正與待確認項目。
2. WRITE 讀取 `templates/crosscheck-result.md` 與 `templates/crosscheck-result.example.md`，以統整修正後的草稿為本，依骨架附加待確認與獨立複核狀態章節並更新報告狀態，在執行目錄產出最終報告 `final.md`，只回傳統整後的最終報告。
