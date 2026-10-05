## 待確認

### {{OPEN_QUESTION_TITLE}}

- 分歧點：{{DISAGREEMENT}}
- 各方主張：{{POSITIONS}}
- 已查證：{{VERIFIED_PART}}
- 缺少的證據：{{MISSING_EVIDENCE}}
- 取得方式：{{HOW_TO_OBTAIN}}

## 獨立複核狀態

<!-- 複核結論只能是：已完成雙重複核、僅完成單一複核（缺少：<reviewer>，原因：<原因>）、未經獨立複核；報告開頭的報告狀態使用相同的值 -->
**複核結論**：{{CROSSCHECK_OUTCOME}}

| Reviewer | 狀態 | 實際執行的檢查 | 驗證限制 |
| --- | --- | --- | --- |
| Subagent | {{SUBAGENT_STATUS}} | {{SUBAGENT_CHECKS}} | {{SUBAGENT_LIMITS}} |
| Codex CLI | {{CODEX_STATUS}} | {{CODEX_CHECKS}} | {{CODEX_LIMITS}} |

- 統整處理：合併 {{MERGED_COUNT}}、採納修正 {{ACCEPTED_FIX_COUNT}}（{{ACCEPTED_FIX_BREAKDOWN}}）、排除 {{EXCLUDED_COUNT}}（{{EXCLUDED_BREAKDOWN}}）、新增 {{ADDED_COUNT}}、待確認 {{OPEN_COUNT}}
- 工作目錄檢查：{{WORKTREE_CHECK}}
- 原始複核結果：{{RAW_RESULT_PATHS}}
