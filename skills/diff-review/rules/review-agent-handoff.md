# Rule 1 - 初審結果寫成兩個檔，驗收合格才可併入報告

- Level: `MUST`
- Agent 把 metadata 寫入 `artifacts.review_meta`（依 `templates/review-agent-result.json`）、審查內容寫入 `artifacts.review`（依 `templates/review-findings.md`），回覆只簡述狀態與路徑。宿主不讓 agent 寫檔時，改由回覆交付兩者的完整內容，主 agent 原樣存成這兩個檔。
- Metadata 必須是可解析的 JSON，欄位齊備：`run_id` 對應本次執行目錄、`status` 為 `completed` 或 `not_completed`、`reason` 為字串，三個來源／判準欄位為字串陣列。
- `completed` 代表初審已完成，審查內容須包含建議修正與審查涵蓋章節；沒有 finding 也須交代涵蓋與限制。必要輸入或核心審查未完成時用 `not_completed` 並寫明原因；個別工具或外部來源未驗證時，依審查規則揭露限制。
- `standards_sources` 只記已讀正文且比對的規範，`requirement_sources` 只記實際讀取的需求檔案；兩者都填純檔案路徑，repo 內用相對路徑，repo 外用絕對路徑。版本註記、只探索適用性的候選及需求原文放在審查章節；需求僅由派發原文提供、沒有來源檔案時，`requirement_sources` 填空陣列。`criteria` 只列本次用於判定程式碼與 findings 的本 skill 規則絕對路徑，包含必讀的 `rules/review-dimensions-and-project-standards.md` 與 `rules/severity-and-findings.md`；React 規則僅在觸發且採用時加入。
- 主 agent 驗收欄位、執行識別、判準路徑存在、來源路徑可讀（repo 內以固定版本確認）與審查內容完整度：每個 finding 有不重複的 F 編號、樣板的全部欄位與圖上節點；納入未提交改動時，涵蓋章節須交代閱讀前與交付前的範圍核對結果。未完成或不合格時揭露原因並停止，不把部分結果包裝成完成初審。
- 驗收通過後，以檔案串接把 `artifacts.review` 原文附加到 `detail.md`，不重新輸出內容；`run.json` 的 `report_kind` 設為 `review`，其餘三個來源／判準陣列保留既有項並加入回傳項、去重，固定範圍與其他欄位保持原值。Metadata 不併入報告，初審不計入獨立複核完成度。

## Good Example

- 初審完成且無 finding，仍交代限制並保留上游判準。

```md
review-agent.json：status=completed，run_id 相符；standards_sources=["AGENTS.md"]，需求僅來自派發原文時 requirement_sources=[]；criteria 列本次採用規則的絕對路徑。
review-agent.md：未發現需修正的問題；已檢查五個核心維度；工具未執行及原因已列出。
寫回：以檔案串接把 review-agent.md 附加到 detail.md；run.json 保留原本的 evidence 與 diagram 判準，再加入初審判準。
```

## Bad Example

- 未完成的初審被當成審查結果，主 agent 又重新抄寫一次內容。

```md
review-agent.json 為 status=not_completed，原因為 head SHA 無法解析。
主 agent 仍把 report_kind 改為 review，並把 agent 回覆的 300 行內容重新打字貼進 detail.md。
```

# Rule 2 - 把初審結果疊回報告本文，不搬運證據

- Level: `MUST`
- 依 `templates/review-report.md` 用 Edit 局部修改 `draft.md`，不整份重寫：
  - 標題改為「Code Review」，狀態列加上 P0–P3 各級數量與一句已執行檢查的摘要。
  - 「一句話」末尾補一句問題集中在哪；沒有 finding 時寫未發現需修正的問題。
  - 依 `run.json` 的 `criteria` 中的圖表規則，把每個 finding 依「圖上節點」寫進節點標籤並換成對應 class；「新增」的節點一併加上，超過節點上限時拆圖；更新圖例與圖說，改動地圖的標題改為「改動地圖＋問題標在節點上」。
  - 「要處理的問題」一則一行：等級、問題（finding 標題的短句）、建議（最小修正方向的短句）、連到 `detail.md` 對應錨點的 F 編號；依嚴重性排序。
  - 「待確認」只列需要他人（後端、PM、設計）回答，且會影響 finding 成立或等級的問題。
  - 「驗證範圍」用「跑過」「沒驗」各一行，取自審查涵蓋。
- 本文不放證據、檢查指令、需求逐條對照或已檢查維度，這些留在詳細檔；本文以約 150 行為上限，超過時先精簡圖的節點與群組表，不刪問題表。

## Good Example

- 本文只多出圖上的標記與一則一行的問題表，細節留在詳細檔。

```md
圖 2：machine 改為 changedMajor，標籤加「⚠ P1 逾時仍清空購物車（F2）」；api 改為 affectedMajor。
要處理的問題：| P1 | 逾時錯誤仍會清空購物車 | 逾時也進入 error 狀態 | [F2](detail.md#f2) |
驗證範圍：跑過「變更檔 ESLint、checkoutMachine 測試 12 項」；沒驗「後端去重、螢幕閱讀器實測」。
```

## Bad Example

- 把詳細檔的完整欄位搬進本文，又另拉問題節點。

```md
## 要處理的問題
#### [P1] 逾時錯誤仍會清空購物車
- 觸發情境：…… - 證據：…… - 檢查指令：`git show ……` - 位置：……
圖 2：新增節點 issue_p1["P1 逾時清空購物車"]，以虛線連到 machine。
```
