## 建議修正

### P0 緊急

#### F1 [P0] 逾時後重試可能重複扣款

- 狀態：待驗證疑慮
- 提出者：草稿
- 維度：正確性、資料完整性
- 觸發情境：付款 API 逾時但實際已扣款 → 使用者點擊重試 → 以同一購物車再次建立訂單。
- 影響：若後端沒有去重，同一筆訂單會被扣款兩次。
- 證據：重試時沿用原購物車並重新呼叫 `createOrder()`，未帶任何冪等鍵【程式碼證實】；後端是否去重無法從 repo 內證實。
- 檢查指令：`git grep -n "createOrder" a1b2c3d4e5f6 -- src/api`
- 位置：[checkoutMachine.ts#L40-L46](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/checkout/checkoutMachine.ts#L40-L46)（重試回到送出中並呼叫 `createOrder()`）、[orderApi.ts#L21-L30](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/api/orderApi.ts#L21-L30)
- 圖上節點：圖 2 `api`
- 依據規範：無
- 最小修正方向：確認後端是否支援 `Idempotency-Key`；支援時在重試請求帶入同一把鍵。
- 備註：缺少證據為後端 API 的去重行為；可詢問後端或在測試環境重現逾時後重試。

### P1 高

#### F2 [P1] 逾時錯誤仍會清空購物車

- 狀態：確定問題
- 提出者：草稿
- 維度：需求符合度、正確性
- 觸發情境：付款 API 回應 504 → 狀態機進入 `TimeoutError` 分支。
- 影響：使用者看到重試按鈕，但購物車已被清空；與驗收情境「付款失敗後購物車內容維持不變」矛盾。
- 證據：新增的 `error` 轉移只涵蓋 `NetworkError` 與 `PaymentDeclined`，`TimeoutError` 分支仍保留修改前的 `clearCart()` 呼叫【程式碼證實】；驗收情境原文「付款失敗時，購物車內容 MUST 維持不變」【需求明訂】`spec.md` Scenario「付款失敗」。
- 檢查指令：`git show a1b2c3d4e5f6:src/checkout/checkoutMachine.ts | sed -n '88,95p'`
- 位置：[checkoutMachine.ts#L88-L95](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/checkout/checkoutMachine.ts#L88-L95)
- 圖上節點：圖 2 `machine`、圖 3 `timeout`
- 依據規範：無（依需求判定）
- 最小修正方向：移除 `TimeoutError` 分支中的 `clearCart()`，讓逾時與其他錯誤一樣進入 `error` 狀態。
- 備註：無

### P2 中

#### F3 [P2] 新增的 `formatPrice` 與既有 `formatCurrency` 承載同一規則

- 狀態：確定問題
- 提出者：草稿
- 維度：複用與 DRY
- 觸發情境：日後幣別或小數位規則調整時，只改其中一份。
- 影響：結帳頁與商品頁顯示的金額格式會不一致。
- 證據：兩者都依 locale 以 `Intl.NumberFormat` 格式化金額、小數位相同，且修改理由相同（金額顯示規則）【程式碼證實】。
- 檢查指令：`git grep -n "Intl.NumberFormat" a1b2c3d4e5f6 -- src`
- 位置：[CartSummary.tsx#L8-L14](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/cart/CartSummary.tsx#L8-L14)、[currency.ts#L3-L11](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/utils/currency.ts#L3-L11)
- 圖上節點：圖 2 `summary`
- 依據規範：`AGENTS.md`「新增元件或工具函式前先搜尋既有實作」
- 最小修正方向：刪除 `formatPrice`，改用 `formatCurrency`。
- 備註：此 repo 的 AGENTS.md 規定重複實作在 push 前審查會被擋下。

### P3 低

#### F4 [P3] `RETRY` 事件以型別斷言送出

- 狀態：確定問題
- 提出者：草稿
- 維度：維護性與單一職責
- 觸發情境：日後改名或移除 `RETRY` 事件時，結帳頁的送出呼叫不會被型別檢查攔下。
- 影響：事件名稱不一致時，重試按鈕沒有反應，且只能在執行期發現。
- 證據：`CheckoutEvent` 型別聯集沒有加入 `RETRY`，結帳頁以 `{ type: 'RETRY' } as CheckoutEvent` 送出【程式碼證實】。
- 檢查指令：`git show a1b2c3d4e5f6:src/checkout/CheckoutPage.tsx | sed -n '60,66p'`
- 位置：[CheckoutPage.tsx#L63](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/checkout/CheckoutPage.tsx#L63)
- 圖上節點：圖 2 `page`
- 依據規範：無
- 最小修正方向：把 `RETRY` 加入 `CheckoutEvent`，移除 `as` 斷言。
- 備註：無

## 審查涵蓋與驗證限制

### 需求符合度

| 驗收條件 | 判定 | 證據 |
| --- | --- | --- |
| 付款失敗後購物車內容維持不變 | 部分實作 | 逾時錯誤仍會清空，見 F2 |
| 失敗後顯示重試按鈕 | 已實作 | [CheckoutPage.tsx#L60-L66](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/checkout/CheckoutPage.tsx#L60-L66) |
| 重試不得重複扣款 | 未驗證 | 需確認後端去重行為，見 F1 |

### 已檢查維度

- 核心維度：正確性、需求符合度、專案規範、複用與 DRY、維護性與單一職責
- 條件維度：a11y（觸發：新增重試按鈕與錯誤提示）、外部契約（觸發：重試會再次呼叫訂單 API）、資料完整性（觸發：重試可能重複建立訂單）；安全性、效能未觸發
- 已讀規範：`AGENTS.md`、`.cursor/rules/a11y.mdc`、`.eslintrc.cjs`（判斷工具已強制的項目）
- 探索到但未逐條比對：`.claude/skills/frontend-standards/SKILL.md`（與本次改動無直接相關）

### 已執行檢查

| 檢查 | 結果 | 備註 |
| --- | --- | --- |
| CI（`gh pr checks 482`） | 全部通過 | 針對 head `a1b2c3d4e5f6` |
| Vitest（`checkoutMachine.test.ts`、`useCart.test.ts`） | 12 項全部通過 | 以 `git archive a1b2c3d4e5f6` 匯出 head 至暫存目錄執行，`node_modules` 以 symlink 共用、快取指向匯出目錄，依賴宣告與 head 相同，`node_modules/.vite` 前後無變動 |
| ESLint（6 個變更檔） | 0 個問題 | 同上，在 head 匯出目錄執行 |
| 型別檢查 | 未執行 | CI 已包含型別檢查且通過 |

### 未驗證項目

- 後端訂單 API 是否以冪等鍵去重。
- 錯誤提示在螢幕閱讀器上的實際播報（需在瀏覽器手動確認）。

### 既有問題（非本次引入）

- `cartSlice.ts` 有 2 個既有的 `any`，本次未修改，未列入建議修正。
