<!-- final.md：狀態列開頭的粗體改為複核結論，結尾的詳細檔指引改指向 final-detail.md，並在「驗證範圍」最後加入下一行；沒有「驗證範圍」（report_kind 為 explain）時，在結尾的詳細檔指引前新增「## 驗證範圍」並只放這一行。需要新增待確認問題而沒有「待確認」時，在「驗證範圍」前新增「## 待確認」 -->
- **複核**：Subagent {{SUBAGENT_STATUS}}、Codex {{CODEX_STATUS}}（{{CODEX_MODEL_SUMMARY}}）；{{CONSOLIDATION_SUMMARY}}；工作目錄{{WORKTREE_CHECK_SUMMARY}}

<!-- final-detail.md：以下章節附加在檔尾；沒有待確認時刪除「待確認」整節 -->
## 待確認

### {{OPEN_QUESTION_TITLE}}

- 分歧點：{{DISAGREEMENT}}
- 各方主張：{{POSITIONS}}
- 已查證：{{VERIFIED_PART}}
- 缺少的證據：{{MISSING_EVIDENCE}}
- 取得方式：{{HOW_TO_OBTAIN}}

## 獨立複核紀錄

**複核結論**：{{CROSSCHECK_OUTCOME}}

| Reviewer | 狀態 | 實際執行的檢查 | 驗證限制 |
| --- | --- | --- | --- |
| Subagent | {{SUBAGENT_STATUS}} | {{SUBAGENT_CHECKS}} | {{SUBAGENT_LIMITS}} |
| Codex CLI | {{CODEX_STATUS}} | {{CODEX_CHECKS}} | {{CODEX_LIMITS}} |

- Codex 模型與重試：{{CODEX_ATTEMPTS}}
- 統整處理：合併 {{MERGED_COUNT}}、採納修正 {{ACCEPTED_FIX_COUNT}}（{{ACCEPTED_FIX_BREAKDOWN}}）、排除 {{EXCLUDED_COUNT}}（{{EXCLUDED_BREAKDOWN}}）、新增 {{ADDED_COUNT}}、待確認 {{OPEN_COUNT}}
- 工作目錄檢查：{{WORKTREE_CHECK}}
- 原始複核結果：{{RAW_RESULT_PATHS}}
