---
name: diff-crosscheck
description: 對 diff-explain 或 diff-review 產出的執行目錄（含固定 base / head SHA 的 run.json、報告本文與詳細檔），平行交由一個獨立唯讀 subagent 與 Codex CLI 複核，再由主 agent 對照程式碼重新查證、在副本上修正成最終報告。由 diff-review 串接，或使用者提供執行目錄並要求「雙重複核」「第二意見」「用 Codex 複核」「cross-check 這份報告」時使用；沒有執行目錄時，先用 diff-explain 或 diff-review 建立。
---

# Diff 獨立雙重複核

讓兩個彼此隔離的 reviewer 以相同的固定範圍複核同一份草稿，再由主 agent 對照程式碼統整；所有人類可讀輸出使用繁體中文。

文中的 `rules/`、`templates/`、`scripts/` 路徑皆相對於本 skill 目錄；腳本只用 Python 標準函式庫，預設以 `uv run` 執行，`uv` 不可用時改用 `python3`。

# SOP

## Phase 1 -- 確認複核輸入

1. READ 讀取執行目錄的 `run.json`、`draft.md` 與 `detail.md`，確認 repo、base / head SHA、比較方式、`report_kind`、`diff.patch`、`criteria` 與 `tools.render_mermaid` 齊備且 SHA 仍可解析（`mode` 為 `direct` 時 `merge_base` 可以為空）；缺漏時向使用者說明並停止。

## Phase 2 -- 完成獨立雙重複核

1. WRITE 讀取 `rules/reviewer-dispatch-and-independence.md` 與 `templates/reviewer-brief.md`，依規則與骨架以 `run.json`、`draft.md` 與 `detail.md` 的內容改寫填位符號，在執行目錄產出兩個 reviewer 共用的 `reviewer-brief.md`；格式有疑問時才參照 `templates/reviewer-brief.example.md`。
2. DELEGATE 執行 `uv run scripts/check_worktree.py --repo <受審 repo> --save <reviews_dir>/worktree-before.json` 記錄工作目錄快照（`<reviews_dir>` 為 `run.json` 的 `artifacts.reviews_dir`），在系統暫存目錄另建 subagent 專用的私有目錄，再依已載入規則平行啟動 subagent（交付 `reviewer-brief.md` 與私有目錄中結果檔的路徑）與在背景執行 `uv run scripts/run_codex_review.py --repo <受審 repo> --brief <reviewer-brief.md>` 的 Codex 複核。
3. DELEGATE Codex 狀態 JSON 的 `status` 為 `capacity` 或 `model_unsupported` 時，依已載入規則請使用者選模型；使用者指定後，在背景執行 `uv run scripts/run_codex_review.py --repo <受審 repo> --brief <reviewer-brief.md> --resume <session_id> --model <模型> --out-dir <out_dir>` 接續原 session（狀態 JSON 沒有 `session_id` 時不帶 `--resume`）。
4. READ 兩者都結束後，讀取 subagent 的結果檔與 Codex 狀態 JSON 指向的輸出。
5. WRITE 把兩份結果檔與 Codex 狀態 JSON 移入 `<reviews_dir>`，不重新輸出內容；執行 `uv run scripts/check_worktree.py --repo <受審 repo> --compare <reviews_dir>/worktree-before.json` 確認 reviewer 沒有修改受審 repo；任一方失敗或工作目錄有變動時，依已載入規則記錄並揭露。

## Phase 3 -- 統整並產出最終報告

1. THINK 讀取 `rules/consolidation-criteria.md` 與 `run.json` 的 `criteria` 列出的規則，依查證深度對照程式碼查證兩份複核意見，收斂合併、排除、修正與待確認項目。
2. WRITE 依已載入規則把 `draft.md` 複製為 `final.md`、`detail.md` 複製為 `final-detail.md`，用 Edit 原地套用採納的修正。
3. WRITE 讀取 `templates/crosscheck-result.md`，依骨架更新 `final.md` 的狀態列、驗證範圍與詳細檔指引，並把待確認與獨立複核紀錄附加到 `final-detail.md`；格式有疑問時才參照 `templates/crosscheck-result.example.md`。
4. DELEGATE 圖有修改時，執行 `uv run <run.json 的 tools.render_mermaid> --report <final.md>` 渲染檢查，依已載入的圖表規則修正到通過。
5. WRITE 只回傳最終報告與 `final-detail.md` 路徑。
