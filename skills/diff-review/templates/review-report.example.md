# Code Review：結帳失敗後保留購物車

**草稿（尚未複核）**｜`main` ← `feature/keep-cart-on-failure`（`a1b2c3d4e5f6`）｜6 檔 +142／−38｜**P0 1・P1 1・P2 1・P3 1**｜CI 通過；相關測試 12 項、ESLint 無新增問題

## 一句話

送出訂單失敗後不再清空購物車，改為停在新的失敗頁，讓使用者重試或返回修改；購物車金額計算同時抽成共用 hook。問題集中在兩處：**逾時錯誤仍走舊分支清空購物車**，以及**重試沒帶冪等鍵、可能重複扣款**（待後端確認）。

## 圖 1：送出失敗時，修改前 vs 修改後

```mermaid
%%{init: {"themeVariables": {"clusterBkg": "#ffffff", "clusterBorder": "#cbd5e1"}}}%%
flowchart TB
  subgraph b_["修改前"]
    direction LR
    b_cart["購物車"] --> b_submit["送出訂單"]
    b_submit -->|失敗| b_clear["清空購物車（移除）<br/>回到商品頁重選"]
  end
  subgraph a_["修改後"]
    direction LR
    a_cart["購物車"] --> a_submit["送出訂單"]
    a_submit -->|失敗| a_error["失敗頁：保留購物車<br/>可重試或返回修改"]
    a_error -->|重試| a_retry["以原購物車再次送出"]
  end
  b_ ~~~ a_
  classDef default fill:#f8fafc,stroke:#94a3b8,color:#111
  classDef added fill:#dcfce7,stroke:#15803d,color:#111
  classDef removed fill:#f3f4f6,stroke:#9ca3af,color:#6b7280
  class a_error,a_retry added
  class b_clear removed
```

綠＝新增、灰＝移除。失敗不再把使用者送回商品頁；重試沿用同一份購物車。

## 圖 2：改動地圖＋問題標在節點上

```mermaid
flowchart LR
  page["結帳頁<br/>失敗時顯示重試、返回修改<br/>· P3 RETRY 以型別斷言送出（F4）"] -->|送出／重試| machine["結帳狀態機<br/>失敗改進 error，不再清空購物車<br/>⚠ P1 逾時仍清空購物車（F2）"]
  machine -->|建立訂單| api["訂單 API（未改）<br/>重試時再被呼叫一次<br/>⚠ P0 待驗證：可能重複扣款（F1）"]
  machine -->|失敗時保留| cart["useCart<br/>新增共用金額計算 calcTotal"]
  page --> summary["購物車摘要<br/>改用 calcTotal<br/>⚠ P2 formatPrice 重複既有實作（F3）"]
  summary --> cart
  orderSummary["訂單摘要（未改）<br/>失敗後仍顯示原商品"] -->|讀取 items| cart
  classDef default fill:#f8fafc,stroke:#94a3b8,color:#111
  classDef changed fill:#fef3c7,stroke:#b45309,color:#111
  classDef affected fill:#e0f2fe,stroke:#0369a1,color:#111
  classDef changedMajor fill:#fef3c7,stroke:#dc2626,stroke-width:3px,color:#111
  classDef affectedMajor fill:#e0f2fe,stroke:#dc2626,stroke-width:3px,color:#111
  classDef changedMinor fill:#fef3c7,stroke:#6b7280,stroke-width:2px,stroke-dasharray:5 3,color:#111
  class cart changed
  class orderSummary affected
  class machine,summary changedMajor
  class api affectedMajor
  class page changedMinor
```

底色：黃＝修改、藍＝沒改但受影響。框線：紅色粗框＝有 P0–P2、灰色虛框＝只有 P3。

**看圖重點**：右上的藍底紅框。訂單 API 這次沒改，但新增的重試讓同一份購物車可能送出兩次，原本「一次送出只建立一筆訂單」的前提不再成立。

## 圖 3：送出後的狀態

```mermaid
flowchart TD
  editing["編輯中"] -->|送出| submitting["送出中"]
  submitting -->|成功| done["完成"]
  submitting -->|網路錯誤、付款被拒| error["送出失敗<br/>保留購物車，可重試"]
  submitting -->|逾時| timeout["逾時：清空購物車<br/>回到編輯中（未改）<br/>⚠ P1 與驗收條件矛盾（F2）"]
  error -->|重試| submitting
  error --> editing
  timeout --> editing
  classDef default fill:#f8fafc,stroke:#94a3b8,color:#111
  classDef added fill:#dcfce7,stroke:#15803d,color:#111
  classDef affectedMajor fill:#e0f2fe,stroke:#dc2626,stroke-width:3px,color:#111
  class error added
  class timeout affectedMajor
```

綠＝新增；藍底紅框＝沒改但受這次改動影響，且有 P0–P2。新增的 `error` 狀態只接網路錯誤與付款被拒，逾時仍走修改前清空購物車的分支，與這次「失敗後保留購物車」的需求矛盾。

## 改動群組

| 群組 | 類型 | 改了什麼 |
| --- | --- | --- |
| 送出失敗保留購物車 | 行為變更 | 失敗後停在新的失敗頁，可重試或返回修改，購物車不再清空 |
| 購物車金額計算抽成 hook | 重構 | 結帳頁與購物車摘要改用同一份 `calcTotal` |
| 重試文案與測試 | 配套修改 | 新增重試按鈕文案與失敗狀態測試 |

## 要處理的問題

| 等級 | 問題 | 建議 | 詳細 |
| --- | --- | --- | --- |
| P0 | 逾時後重試可能重複扣款（待驗證） | 確認後端是否支援 `Idempotency-Key`，支援就在重試帶同一把鍵 | [F1](detail.md#f1) |
| P1 | 逾時錯誤仍會清空購物車 | 逾時也進入 `error` 狀態，不呼叫 `clearCart()` | [F2](detail.md#f2) |
| P2 | 新增的 `formatPrice` 與既有 `formatCurrency` 重複 | 改用 `formatCurrency` | [F3](detail.md#f3) |
| P3 | `RETRY` 事件以型別斷言送出 | 把 `RETRY` 加入 `CheckoutEvent` | [F4](detail.md#f4) |

## 待確認

- 後端訂單 API 會不會以訂單 ID 或冪等鍵去重？（決定 F1 是否成立）

## 驗證範圍

- **跑過**：CI（head `a1b2c3d4e5f6`）全部通過；相關 2 個測試檔 12 項、6 個變更檔 ESLint，都沒有新增問題。
- **沒驗**：後端去重行為、錯誤提示在螢幕閱讀器上的播報。

> 比較範圍、完整 findings 與審查涵蓋在 `detail.md`，需要追查時再看。
