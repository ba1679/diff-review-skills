# Rule 1 - 兩個 reviewer 使用同一份 brief 與全新 context

- Level: `MUST`
- 依 reviewer brief 樣板填入 `run.json` 與草稿的資料，保留完整限制；兩方只收到同一份 brief，不另加主 agent 的推理、對話摘要或懷疑清單。
- subagent 使用全新 context，不 fork 或延續主對話；只交付 brief 路徑與私有結果檔路徑，要求它把完整回覆寫入該檔、回覆只簡述完成狀態。宿主的 agent 無法寫檔時，改以回覆交付完整內容，由主 agent 原樣存檔。
- 納入未提交改動時，在 brief 的工作目錄說明寫明 head 端包含無法以 SHA 固定的內容、以 `diff.patch` 為權威 diff，並要求回報工作目錄與 patch 的不一致。

## Good Example

- 兩方取得相同資料。

```md
Subagent：請讀取並遵循 /tmp/runs/web-a1b2c3d/reviewer-brief.md，把完整結果寫入 /tmp/subagent-review-k3j9/subagent.md，回覆只需說明是否完成。
Codex：由腳本讀取同一份 reviewer-brief.md。
```

## Bad Example

- 單方加料會引導結論。

```md
Subagent：請讀取 brief。另外我覺得 P1 那條可能誤判，請特別確認。
```

# Rule 2 - 完成前隔離兩方輸出

- Level: `MUST`
- 兩者都完成或確定失敗前，不互傳結果，brief 也不列出另一方的輸出位置。
- 讀取範圍限 brief 列出的輸入與受審 repo。Codex 輸出使用腳本的私有暫存目錄，subagent 結果寫入主 agent 另建的私有暫存目錄；兩者都結束後，才把結果檔移入 `run.json` 的 `artifacts.reviews_dir`。

## Good Example

- 共用輸入中沒有 reviewer 輸出。

```md
Codex：輸出留在腳本建立的私有暫存目錄。
Subagent：結果寫入主 agent 另建的私有暫存目錄，路徑只出現在派發給它的訊息中。
兩方結束後：主 agent 才把兩份結果檔移入 reviews_dir。
```

## Bad Example

- 後啟動的一方已受到另一方影響。

```md
Codex 已完成，請 subagent 先讀 codex-review.md，再補充遺漏。
```

# Rule 3 - 驗收唯讀執行，違反時停用該方結果

- Level: `MUST`
- reviewer 的唯讀與安全衛生限制依 brief 交付；Codex 由腳本強制唯讀 sandbox，並查核 session 每一輪的實際 sandbox。
- 工作目錄快照不一致時，揭露變動與造成者（可判斷時）；已確認違反者或回傳 `unsafe_sandbox` 的 Codex，其結果標為不可信並依 Rule 4 視為未完成。
- 變動交由使用者決定如何處理，不自行還原使用者的檔案。

## Good Example

- 停用違反者的結果，保留檔案供使用者處置。

```md
複核後：確認 subagent 修改了 useCart.ts。
處置：subagent 結果標為不可信；請使用者決定是否保留修改，未自行還原。
```

## Bad Example

- 發現違反唯讀後仍採用結果。

```md
Reviewer 順手修了問題，採用它的複核結果並繼續宣稱雙重複核完成。
```

# Rule 4 - 依有效的獨立結果判定複核完成度

- Level: `MUST`
- reviewer 必須有非空、符合 brief 格式且未被 Rule 3 停用的結果才算完成；Codex 另須狀態 JSON 為 `completed`。
- Codex 重試由腳本負責，主 agent 不自行從頭重跑；`capacity` 與 `model_unsupported` 依 Rule 5 處理，其他未完成狀態揭露 JSON 的 `reason` 與 `action`。Subagent 逾時或崩潰可重啟一次，仍失敗就記錄原因。
- 主 agent 的意見不算獨立複核；宿主缺少 subagent 能力時標示未執行，改用其他獨立 reviewer 須經使用者同意。
- 兩方都結束或確定失敗後，依有效結果數判定報告狀態與複核結論：兩份為「已完成雙重複核」；一份為「僅完成單一複核（缺少：<reviewer>，原因：<原因>）」；零份為「未經獨立複核」。

## Good Example

- 揭露缺少的結果與原因。

```md
僅完成單一複核（缺少：Codex CLI，原因：未登入）
Subagent：完成；Codex CLI：未完成（auth），建議執行 codex login。
```

## Bad Example

- 有輸出不等於合格回覆。

```md
Codex 狀態為 completed，但只回覆「看起來沒問題」；仍計為完成雙重複核。
```

# Rule 5 - 模型容量不足或不支援時，由使用者決定換模型

- Level: `MUST`
- 自動換模型限使用者預先設定的備援模型，由腳本負責；主 agent 不自行挑選模型或默默降為單一複核。
- 回傳 `capacity`（容量不足且自動重試用盡）或 `model_unsupported`（此帳號不支援該模型）時立即詢問使用者，不必等 subagent：列出 `attempts` 中已嘗試的模型、失敗訊息與 `model_candidates`，說明候選來自 Codex 模型目錄，不保證此帳號可用。
- 使用者指定模型後，依 SOP 接續原 session；`session_id` 與 `out_dir` 取自狀態 JSON，沒有 `session_id` 時改為不帶 `--resume` 重跑。選擇不換時，依 Rule 4 揭露未完成，原因為「模型容量不足」或「模型不支援」。

## Good Example

- 說明可選方案並保留進度。

```md
預設模型 A 回報此帳號不支援（model_unsupported）；候選為模型 B、C（不保證此帳號可用）。
使用者選 B：沿用狀態 JSON 的 session_id 與 out_dir 接續。
使用者不換：揭露 Codex 未完成，原因為模型不支援。
```

## Bad Example

- 擅自換模型且丟棄 session。

```md
Codex 回報模型不支援，狀態卻當成一般失敗，我自行挑另一個模型從頭重跑。
```
