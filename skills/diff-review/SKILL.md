---
name: diff-review
description: 以固定 SHA 的程式碼證據，對 GitHub PR、分支或版本區間（A → B）做完整 code review，交由獨立 subagent 與 Codex CLI 雙重複核後，統整成含 Mermaid 圖解與 P0–P3 建議修正的報告。使用者說「review 這個 PR」「幫我 CR／審查這個分支」「有證據的 code review」「review PR #123」「review main..feature-x」時使用；只想看懂改動改用 diff-explain；單一檔案或片段的快速意見不使用。需要同時安裝 diff-explain 與 diff-crosscheck。
---

# Diff 有證據審查

串接改動理解、審查與獨立雙重複核，只回傳統整後的最終報告；審查標準以受審 repo 自身規範為準，本 skill 提供通用基準，所有人類可讀輸出使用繁體中文。

文中的 `agents/`、`rules/`、`templates/` 路徑皆相對於本 skill 目錄。

# SOP

## Phase 1 -- 建立改動理解

1. DELEGATE 呼叫 `/diff-explain`，交付使用者提供的 PR URL、base / head、比較方式與未提交改動要求，取得執行目錄；若 `diff-explain` 未安裝或範圍固定失敗，向使用者說明原因並停止。

## Phase 2 -- 完成有證據的審查

1. DELEGATE 啟動全新 context 的 review agent，交付 `agents/review-agent.md` 的絕對路徑、執行目錄、使用者需求／驗收條件原文與審查要求，以及已知的完整需求或切片說明（未知就註明），請它唯讀初審並回傳結果；宿主提供唯讀 agent 或 sandbox 時優先使用。
2. WRITE 讀取 `rules/review-agent-handoff.md`，依規則驗收初審結果並將審查內容附加到 `draft.md`，更新標題與 `run.json` 的審查資訊；缺少 subagent 能力、agent 未完成或交接不合格時，揭露原因並停止。

## Phase 3 -- 雙重複核並交付

1. DELEGATE 呼叫 `/diff-crosscheck`，交付執行目錄，取得統整後的最終報告；若 `diff-crosscheck` 未安裝，向使用者說明缺少的複核並提示安裝，把草稿的報告狀態改為「未經獨立複核」後交付。
2. WRITE 只回傳統整後的最終報告。
