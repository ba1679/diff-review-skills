# Rule 1 - 所有意見由主 agent 查證，查證深度依影響決定

- Level: `MUST`
- Findings 的成立、嚴重性與新增問題，以及圖中的改動類型、問題標記與關係，都由主 agent 對照本次固定範圍的程式碼與需求來源親自查證，再套用 `criteria` 決定是否採納；版本讀取與引用依其中的證據規則，包含未提交改動的例外。
- 說明文字的意見只在會改變讀者理解時查證與修正；只涉及數量、措辭或證據格式的意見，能直接從 `diff.patch` 確認就順手修正，否則略過並計入排除。
- 草稿與 reviewer 意見地位相同，票數不決定成立與否。新增 finding 也須親自確認觸發路徑並補齊 `criteria` 要求的證據、位置、圖上節點與修正方向；證據不足者依 Rule 4 列待確認，或依判準排除。

## Good Example

- 程式碼證據優先於票數，查證力氣花在會改變結論的地方。

```md
Codex 認為已有 guard；草稿與 subagent 認為仍有問題。
主 agent 查證：guard 只涵蓋 NetworkError，TimeoutError 仍呼叫 clearCart() → 保留 F2。
Subagent 指出群組表的 i18n key 數量少算 1 個 → 從 diff.patch 直接確認後順手修正，不另追查。
```

## Bad Example

- 多數決取代查證，又把力氣花在不影響結論的細節。

```md
草稿與 subagent 都認為成立，二比一，維持成立。
為了核對一個 i18n key 的數量，逐一讀 node_modules 原始碼與所有呼叫端。
```

# Rule 2 - 依同一問題合併 findings，再全域排序

- Level: `MUST`
- 同一根因造成的同一問題合併為一條，保留完整證據與所有位置；相同位置或修正方向只作輔助，不能單獨作為合併條件。合併後沿用其中最小的 F 編號，其餘編號不再使用。
- 標示提出者：草稿、Subagent、Codex；多方獨立提出者另標「多方佐證」。依 `criteria` 重判嚴重性與影響後，全域重新排序。

## Good Example

- 同一根因跨位置呈現，保留證據與來源。

```md
F2 [P1] 逾時仍清空購物車（提出者：草稿、Codex；多方佐證）
位置：checkoutMachine.ts#L88-L95；CheckoutPage.tsx#L52（呼叫端）。
```

## Bad Example

- 同一位置的不同問題被誤合併。

```md
同一行同時缺少權限檢查與輸入驗證，因位置相同而合併成一條 finding。
```

# Rule 3 - 在副本上原地修正，不整份重寫

- Level: `MUST`
- 先把 `draft.md` 複製為 `final.md`、`detail.md` 複製為 `final-detail.md`，再用 Edit 局部修改；不重新輸出整份報告，也不手動重抄 reviewer 的原始結果。
- 把 `final.md` 問題表中的詳細檔連結改指向 `final-detail.md` 的對應 finding 錨點；合併或排除時同步更新連結，確認每個連結都能定位到保留的 finding。
- 查證屬實的圖、群組與說明問題直接修正；finding 新增、合併、改級或排除時，同步修改 `final-detail.md` 的 finding、`final.md` 的問題表、狀態列的各級數量，以及圖上的標籤與 class。證據標記與變更／影響範圍依 `criteria` 校正，不以文末勘誤保留錯誤版本。
- 新增的 finding 依 findings 樣板的欄位寫入 `final-detail.md`，提出者標 Subagent 或 Codex。
- 不符合 `criteria` 的意見排除，依結果樣板在 `final-detail.md` 記錄數量與類型；偏好類不必逐條列出。

## Good Example

- 只改有變動的地方，本文、圖與詳細檔保持一致。

```md
複製：draft.md → final.md；detail.md → final-detail.md
Edit final.md：圖 2 的 summary 由 changedMajor 改為 changedMinor，標籤「⚠ P2」改為「· P3」；問題表 F3 改為 P3，詳細連結改為 [F3](final-detail.md#f3)；狀態列 P2 1→0、P3 1→2
Edit final-detail.md：F3 的嚴重性改為 P3 並寫明理由；排除 3 項：不成立 1、個人偏好 2
```

## Bad Example

- 整份重寫，錯誤版本仍留在本文。

```md
依草稿與兩份複核結果重新輸出整份 final.md。
註：reviewer 指出 F3 應為 P3。（圖與問題表未修改）
```

# Rule 4 - 無法判定的意見列待確認，保留仍成立的疑慮

- Level: `MUST`
- 查證後仍缺執行期、需求或外部系統證據的意見與分歧，依結果樣板列入 `final-detail.md` 的「待確認」，交代各方主張、已查證部分與取得缺少證據的方式；需要他人回答的，在 `final.md` 的「待確認」加一行問題；沒有這一節時，在「驗證範圍」（沒有時改為結尾的詳細檔指引）前新增。
- 對象若仍符合 finding 成立條件，保留該 finding 並維持待驗證狀態，同時與「待確認」互相引用。

## Good Example

- 缺口具體，符合條件的疑慮仍可見。

```md
final.md 問題表：P0 逾時後重試可能重複扣款（待驗證）｜[F1](final-detail.md#f1)
final.md 待確認：後端訂單 API 會不會以冪等鍵去重？（決定 F1 是否成立）
final-detail.md 待確認：前端未帶冪等鍵；Codex 主張後端去重，但未提供證據；需後端 API 文件或測試環境重現；參見 F1。
```

## Bad Example

- 尚未判定就刪除疑慮。

```md
後端是否去重無法確認，所以刪除 F1，也不列待確認。
```

# Rule 5 - 複核狀態忠於實際執行，驗證缺口向下傳遞

- Level: `MUST`
- 複核結論依已載入的派發規則判定，寫在 `final.md` 狀態列開頭；結果樣板的 reviewer 狀態填「完成、未完成、未執行」，未完成時附原因。
- `final.md` 只依結果樣板在「驗證範圍」加一行複核摘要（各方狀態、Codex 模型與重試、複核後的主要變動、工作目錄檢查）；reviewer 的檢查與限制、統整統計與原始結果路徑寫在 `final-detail.md`，原始複核全文不併入。
- 檢查與限制依 reviewer 實際回報填寫，Codex 模型與重試經過取自狀態 JSON 的 `attempts`；任一方未驗證的面向，最終報告不得寫成已驗證。

## Good Example

- 完成複核仍保留驗證限制。

```md
final.md 狀態列：**已完成雙重複核**｜……
final.md 驗證範圍：- **複核**：Subagent 完成、Codex 完成（預設模型不支援，改用使用者選的模型 B 接續）；複核後新增 F5；工作目錄前後一致
final-detail.md：兩方都未執行測試 → 記錄未執行測試。
```

## Bad Example

- 未驗證被寫成通過。

```md
Reviewer 無法讀取 Jira 需求，最終報告卻寫「需求符合度已驗證」。
```
