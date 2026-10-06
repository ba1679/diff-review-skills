# Rule 1 - 重要結論必須標示證據等級

- Level: `MUST`
- 重要的行為、需求與必要性結論，依下列分類標示；同一結論可共用一組標記與來源：
  - 【程式碼證實】：讀過固定版本的程式碼或測試斷言直接支持，附位置連結、可重現的唯讀指令，或指出 `diff.patch` 中的 hunk。
  - 【需求明訂】：使用者需求、PR 描述、issue、規格或驗收條件明文寫出，附來源位置；涉及用詞判定時引用原文。
  - 【推測】：由命名、註解、commit message、慣例或間接跡象推論，寫出依據與驗證方式。
- PR 描述或作者對行為、測試結果的宣稱，查證前標為【推測】。
- 測試斷言支持其涵蓋的預期行為；直接對應明文驗收條件時，可連同該條件作需求證據。
- 引用 CI 或工具結果時，記錄取得方式與對應 commit；納入未提交改動時記錄工作目錄指紋。

## Good Example

```md
- 送出前會先移除空白項目【程式碼證實】[useCart.ts#L40-L46](https://github.com/acme/web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/cart/useCart.ts#L40-L46)
- 需求要求「購物車不可出現數量為 0 的商品」【需求明訂】PR 描述第 2 點
- 改用 Map 可能是為了效能【推測】依據：commit message 寫 "perf"；可比對修改前後的查找次數驗證
```

## Bad Example

```md
- 這次改動修正了數量為 0 的 bug，並改善了效能。
```

# Rule 2 - 以 diff 為入口，按結論需要擴大閱讀

- Level: `SHOULD`
- 以 `diff.patch` 的檔案清單（含 rename）與各 hunk 為入口，擴讀以支持待說明的行為或必要性為目的。以下為常見情境，閱讀與引用聚焦於足以支持結論的區段：
  - 改了函式、hook、元件、型別或 API 的簽名或回傳形狀 → 讀相關呼叫端、mock、fixture 或測試替身。
  - 刪除或改名 export、設定 key、i18n key、CSS class、test id、路由、事件名稱，或改了元件的無障礙角色、名稱或可見文字 → 搜尋相關引用，包含測試、e2e 定位器與設定檔。
  - 改了共用模組或 util 的行為 → 讀主要呼叫者，理解受影響的使用情境。
  - 改了條件分支、狀態轉移或錯誤處理 → 比對修改前版本，按需追查相關入口路徑。
  - 改動依賴外部契約（API 回應、postMessage、storage schema、URL 參數、事件 payload） → 讀契約定義或另一端的實作。

## Good Example

```md
待說明：`useCart` 新增的 `errors` 用在哪裡
擴讀：git grep -n "useCart" <head SHA> -- src tests
發現：src/checkout/CheckoutPanel.tsx 使用 `errors` 顯示欄位錯誤
```

## Bad Example

```md
新增的 `errors` 欄位寫法正確，型別也有定義，沒有問題。
```

# Rule 3 - 按需查找需求來源與 PR 背景

- Level: `SHOULD`
- 需求來源以使用者在對話中提供的內容為優先；其他來源按與本次改動的相關性查找：
  - PR 描述、PR 連結的 issue 與 PR 討論。
  - repo 內與 branch 名稱、ticket key 或改動功能對應的規格與設計文件，例如 `specs/`、`docs/`。
- 使用 OpenSpec 時，以變更檔案、功能名稱或 ticket key 定位相關 change：`openspec/changes/<change>/specs/**/spec.md` 的 Scenario 提供驗收情境，`design.md` 提供設計背景；`openspec/specs/` 用於對照已定案的現況。
- 引用 PR 的流程或圖表時，按待說明的結論核對實作；有落差時列出差異與來源位置。
- 無法讀取的需求來源，記錄來源與原因。

## Good Example

```md
PR 附圖：送出失敗後回到「編輯中」狀態
實作：失敗後進入 `error` 狀態，需手動點擊重試才回到編輯【程式碼證實】[checkoutMachine.ts#L88-L95](https://github.com/acme/web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/checkout/checkoutMachine.ts#L88-L95)
落差：附圖與實作不一致，以程式碼為準
```

## Bad Example

```md
依 PR 附圖，送出失敗後會回到編輯中狀態。（未讀取實作）
```

# Rule 4 - 程式碼讀取與引用必須對應固定版本

- Level: `MUST`
- 搜尋與閱讀以 `run.json` 固定的 SHA 為準，例如 `git grep -n <pattern> <head SHA>`、`git show <base SHA>:<path>`；引用前確認對應版本與行號。
- `run.json` 的 `repo.link_base` 不為空時，用它組成完整 SHA 的 permalink：`<link_base>/<完整 SHA>/<path>#L<a>-L<b>`。
- 新增或修改後的行使用 head SHA；被刪除或修改前的行使用 base SHA（merge-base 模式用 merge-base SHA）。
- `repo.link_base` 為空時，使用 `path:line`，並註明「行號以 <引用版本短 SHA> 為準」。
- 本次納入未提交改動時，head 端改在工作目錄搜尋與閱讀，例如 `git grep -n --untracked <pattern>`；被修改或新增的行引用為 `path:line（工作目錄，指紋 <fingerprint 前 12 碼>）`，指紋取自 `run.json` 的 `uncommitted.fingerprint`；base 端與未修改的行仍使用固定 SHA。

## Good Example

```md
修改後：[useCart.ts#L40-L46](https://github.com/acme/web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/cart/useCart.ts#L40-L46)
修改前：[useCart.ts#L35-L39](https://github.com/acme/web/blob/1234567890abcdef1234567890abcdef12345678/src/cart/useCart.ts#L35-L39)
未提交：src/cart/useCart.ts:40（工作目錄，指紋 9f8e7d6c5b4a）
```

## Bad Example

```md
[useCart.ts:40](https://github.com/acme/web/blob/feature/cart/src/cart/useCart.ts#L40)
```
