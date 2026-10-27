# 改動說明：結帳失敗後保留購物車

**草稿（尚未複核）**｜`main` ← `feature/keep-cart-on-failure`（`a1b2c3d4e5f6`）｜6 檔 +142／−38

## 一句話

送出訂單失敗後不再清空購物車，改為停在新的失敗頁，讓使用者重試或返回修改；購物車金額計算同時抽成共用 hook。重試會不會重複扣款，取決於後端是否去重【推測】。

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

## 圖 2：改動地圖

```mermaid
flowchart LR
  page["結帳頁<br/>失敗時顯示重試、返回修改"] -->|送出／重試| machine["結帳狀態機<br/>失敗改進 error，不再清空購物車"]
  machine -->|建立訂單| api["訂單 API（未改）<br/>重試時再被呼叫一次"]
  machine -->|失敗時保留| cart["useCart<br/>新增共用金額計算 calcTotal"]
  page --> summary["購物車摘要<br/>改用 calcTotal"]
  summary --> cart
  orderSummary["訂單摘要（未改）<br/>失敗後仍顯示原商品"] -->|讀取 items| cart
  classDef default fill:#f8fafc,stroke:#94a3b8,color:#111
  classDef changed fill:#fef3c7,stroke:#b45309,color:#111
  classDef affected fill:#e0f2fe,stroke:#0369a1,color:#111
  class page,machine,cart,summary changed
  class api,orderSummary affected
```

黃＝修改、藍＝沒改但受影響。訂單 API 與訂單摘要這次都沒改：前者在重試時會再被呼叫一次，後者在失敗後會繼續顯示原本的商品。

## 圖 3：送出後的狀態

```mermaid
flowchart TD
  editing["編輯中"] -->|送出| submitting["送出中"]
  submitting -->|成功| done["完成"]
  submitting -->|網路錯誤、付款被拒| error["送出失敗<br/>保留購物車，可重試"]
  submitting -->|逾時| timeout["逾時：清空購物車<br/>回到編輯中（未改）"]
  error -->|重試| submitting
  error --> editing
  timeout --> editing
  classDef default fill:#f8fafc,stroke:#94a3b8,color:#111
  classDef added fill:#dcfce7,stroke:#15803d,color:#111
  class error added
```

綠＝新增。新增的 `error` 狀態只接網路錯誤與付款被拒；逾時仍走修改前的分支。

## 改動群組

| 群組 | 類型 | 改了什麼 |
| --- | --- | --- |
| 送出失敗保留購物車 | 行為變更 | 失敗後停在新的失敗頁，可重試或返回修改，購物車不再清空 |
| 購物車金額計算抽成 hook | 重構 | 結帳頁與購物車摘要改用同一份 `calcTotal` |
| 重試文案與測試 | 配套修改 | 新增重試按鈕文案與失敗狀態測試 |

> 比較範圍與逐項證據在 `detail.md`，需要追查時再看。
