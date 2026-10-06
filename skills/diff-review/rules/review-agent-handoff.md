# Rule 1 - 合格的初審交接才可寫回草稿

- Level: `MUST`
- 回覆依 `templates/review-agent-result.md` 的 metadata 與審查內容兩部分交付。Metadata 必須是可解析的 JSON，欄位齊備：`run_id` 對應本次執行目錄、`status` 為 `completed` 或 `not_completed`、`reason` 為字串，三個來源／判準欄位為字串陣列。
- `completed` 代表初審已完成，審查內容須包含建議修正與審查涵蓋章節；沒有 finding 也須交代涵蓋與限制。必要輸入或核心審查未完成時用 `not_completed` 並寫明原因；個別工具或外部來源未驗證時，依審查規則揭露限制。
- `standards_sources` 只記已讀正文且比對的規範，`requirement_sources` 只記實際讀取的需求檔案；兩者都填純檔案路徑，repo 內用相對路徑，repo 外用絕對路徑。版本註記、只探索適用性的候選及需求原文放在審查章節；需求僅由派發原文提供、沒有來源檔案時，`requirement_sources` 填空陣列。`criteria` 只列本次用於判定程式碼與 findings 的本 skill 規則絕對路徑，包含必讀的 `rules/review-dimensions-and-project-standards.md` 與 `rules/severity-and-findings.md`；React 規則僅在觸發且採用時加入。
- 主 agent 驗收欄位、執行識別、判準路徑存在、來源路徑可讀（repo 內以固定版本確認）與審查章節完整度；納入未提交改動時，涵蓋章節須交代閱讀前與交付前的範圍核對結果。未完成或不合格時揭露原因並停止，不把部分結果包裝成完成初審。
- 驗收通過後，只將審查內容附加到 `draft.md`，把報告標題的「改動說明」改為「Code Review 報告」；`run.json` 的 `report_kind` 設為 `review`，其餘三個來源／判準陣列保留既有項並加入回傳項、去重，固定範圍與其他欄位保持原值。Metadata 不附加到報告本文，初審不計入獨立複核完成度。

## Good Example

- 初審完成且無 finding，仍交代限制並保留上游判準。

```md
Metadata：status=completed，run_id 相符；standards_sources=["AGENTS.md"]，需求僅來自派發原文時 requirement_sources=[]；criteria 列本次採用規則的絕對路徑。
審查內容：未發現需修正的問題；已檢查五個核心維度；工具未執行及原因已列出。
寫回：附加審查章節，保留原本的 evidence 與 diagram 判準，再加入初審判準。
```

## Bad Example

- 未完成初審卻把改動說明當成審查報告。

```md
Agent 回覆 status=not_completed，原因為 head SHA 無法解析。
主 agent 仍把 report_kind 改為 review，並繼續獨立複核。
```
