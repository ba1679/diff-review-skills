# 詳細證據：結帳失敗後保留購物車

## 比較範圍

| 項目 | 內容 |
| --- | --- |
| Repository | acme/shop-web（`/Users/dev/shop-web`） |
| Base | `main` → `3f9c2a7e1b4d`（PR #482 回報的 base） |
| Head | `feature/keep-cart-on-failure` → `a1b2c3d4e5f6`（PR #482 回報的 head） |
| Merge-base | `7e6f5d4c3b2a` |
| 比較方式 | merge-base 比較：`git diff 3f9c2a7e1b4d...a1b2c3d4e5f6` |
| 未提交改動 | 未包含 |
| 規模 | 6 個檔案，+142 / -38，4 個 commit |
| PR | [#482](https://github.com/acme/shop-web/pull/482)：範圍來源與需求來源 |
| 需求來源 | PR #482 描述（3 項驗收條件）；`openspec/changes/keep-cart-on-failure/specs/checkout/spec.md` |
| 備註 | 已執行 `git fetch origin pull/482/head` 取得 head commit；目前 checkout 為 `main`，程式碼一律以固定 SHA 讀取 |

## 改動證據

| 群組 | 主要位置 | 涵蓋檔案 |
| --- | --- | --- |
| 送出失敗保留購物車 | 修改前錯誤轉移呼叫 `clearCart()`【程式碼證實】[checkoutMachine.ts#L52-L58](https://github.com/acme/shop-web/blob/7e6f5d4c3b2a19081726354a5b6c7d8e9f012345/src/checkout/checkoutMachine.ts#L52-L58)；修改後新增 `error` 狀態與 `RETRY`【程式碼證實】[checkoutMachine.ts#L80-L97](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/checkout/checkoutMachine.ts#L80-L97) | `checkoutMachine.ts`、`CheckoutPage.tsx` |
| 購物車金額計算抽成 hook | `calcTotal` 由購物車摘要移到 `useCart`【程式碼證實】[useCart.ts#L12-L28](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/cart/useCart.ts#L12-L28) | `useCart.ts`、`CartSummary.tsx` |
| 重試文案與測試 | `zh-TW.json` 新增 2 個 key；`checkoutMachine.test.ts` 新增 3 個案例【程式碼證實】`diff.patch` | `zh-TW.json`、`checkoutMachine.test.ts` |

### 重構一致性

- 購物車金額計算抽成 hook：預期一致的行為為 `calcTotal` 的輸入輸出、四捨五入方式、空購物車回傳 0、折扣套用順序；支持證據：修改前後的計算與四捨五入邏輯相同【程式碼證實】[修改前 CartSummary.tsx#L20-L34](https://github.com/acme/shop-web/blob/7e6f5d4c3b2a19081726354a5b6c7d8e9f012345/src/cart/CartSummary.tsx#L20-L34)、[修改後 useCart.ts#L12-L28](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/cart/useCart.ts#L12-L28)；尚未證實：折扣為負數的錯誤路徑沒有測試涵蓋。

### 沒改但受影響

- 訂單 API（`api`）：未修改，但新增的 `RETRY` 回到送出中，會以同一份購物車再次呼叫 `createOrder()`【程式碼證實】[checkoutMachine.ts#L40-L46](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/checkout/checkoutMachine.ts#L40-L46)
- 訂單摘要（`orderSummary`）：未修改，但讀取 `useCart().items`，失敗後 items 不再清空【程式碼證實】[Summary.tsx#L12](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/checkout/Summary.tsx#L12)

### 推測與資訊缺口

- 重試會不會重複扣款【推測】依據：重試沿用原購物車再次呼叫 `createOrder()`，未帶冪等鍵；驗證方式：確認後端是否以冪等鍵或訂單 ID 去重
