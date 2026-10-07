# Rule 1 - 一句話與分組以主要行為或功能為主

- Level: `SHOULD`
- 一句話說明改了什麼，以使用者或呼叫端可觀察的變化為主；動機未確認時，不寫推論出的目的。
- 群組依功能、使用者行為或模組責任組織；次要與配套改動可併入相關群組。

## Good Example

```md
送出失敗後不再清空購物車，改為停在失敗頁讓使用者重試或返回修改；購物車金額計算同時抽成共用 hook。
```

## Bad Example

```md
為了提升使用者滿意度並降低流失率，結帳流程全面優化。
```

# Rule 2 - 分類並交代所有改動

- Level: `MUST`
- 每組標示類型：
  - 行為變更：使用者或呼叫端可觀察到的行為、輸出、狀態或錯誤處理有所改變。
  - 重構：預期行為不變的結構調整。
  - 配套修改：為支撐上述改動而做的測試、型別、設定、文件、i18n、樣式或依賴更新。
- diff 中每個檔案都須在詳細檔的「改動證據」歸入群組；同一檔案可分屬多組；同一目錄的檔案全屬一組時，可用目錄或 glob 加檔案數概括；lock file、產生檔可簡述為配套修改。
- 同組包含不同類型時標示各部分，例如「行為變更，含重構與配套修改」；含行為變更的群組以行為變更標示。

## Good Example

```md
本文：
| 群組 | 類型 | 改了什麼 |
| --- | --- | --- |
| 送出失敗保留購物車 | 行為變更 | 失敗後停在新的失敗頁，可重試或返回修改 |
| 購物車金額計算抽成 hook | 重構 | 結帳頁與購物車摘要改用同一份 `calcTotal` |
| 重試文案與測試 | 配套修改 | 新增重試按鈕文案與失敗狀態測試 |

詳細檔「改動證據」的涵蓋檔案：checkoutMachine.ts、CheckoutPage.tsx｜useCart.ts、CartSummary.tsx｜zh-TW.json、checkoutMachine.test.ts
```

## Bad Example

```md
- src/checkout/：改了 3 個檔案
- src/cart/：改了 2 個檔案
- tests/：改了 1 個檔案
```

# Rule 3 - 群組表一組一行，證據放詳細檔

- Level: `MUST`
- 報告本文的群組表一組一行；「改了什麼」用一句話寫可觀察的行為或結構變化，目的只在已確認且能補充資訊時併入同一句。
- 本文不放證據、連結或檔案清單；未證實的敘述標【推測】。
- 詳細檔的「改動證據」為每組列出主要位置與涵蓋檔案，讓本文每一列都能被查證。
- 目的或必要性無法確認時，本文只寫已知行為，資訊缺口列在詳細檔。

## Good Example

```md
本文：| 送出失敗保留購物車 | 行為變更 | 失敗後停在新的失敗頁，可重試或返回修改，購物車不再清空 |
詳細檔：| 送出失敗保留購物車 | [checkoutMachine.ts#L80-L97](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/checkout/checkoutMachine.ts#L80-L97) | checkoutMachine.ts、CheckoutPage.tsx |
```

## Bad Example

```md
| 送出失敗保留購物車 | 行為變更 | 目的：送出失敗時保留商品【程式碼證實】[checkoutMachine.ts#L80-L97](...)。必要性：原本會清空購物車【程式碼證實】[checkoutMachine.ts#L52-L58](...)。不改的後果：使用者需重新選購。 |
```

# Rule 4 - 重構結論必須有一致性證據

- Level: `MUST`
- 在詳細檔說明與本次重構相關、預期保持一致的行為，並附支持證據；可按輸入輸出、副作用、錯誤路徑、呼叫順序或公開介面選取相關面向。
- 支持證據可包含前後邏輯對照，或覆蓋相關行為的測試斷言與執行結果。
- 影響結論的重要部分尚未證實時，列出該部分與缺少的證據。

## Good Example

```md
預期一致：`calcTotal` 的輸入輸出、四捨五入方式、空購物車回傳 0。
支持證據：前後版本的計算邏輯相同【程式碼證實】[修改前 CartSummary.tsx#L20-L34](https://github.com/acme/shop-web/blob/7e6f5d4c3b2a19081726354a5b6c7d8e9f012345/src/cart/CartSummary.tsx#L20-L34)、[修改後 useCart.ts#L12-L28](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/cart/useCart.ts#L12-L28)。
尚未證實：折扣為負數的錯誤路徑沒有測試涵蓋。
```

## Bad Example

```md
這只是把計算邏輯抽成 hook，純重構，行為不變。
```

# Rule 5 - 以圖為主，依改動特徵選圖

- Level: `SHOULD`
- 報告以圖說明改動，依改動特徵選擇，最多三張，依序編號：
  - 修改前 vs 修改後：使用者或呼叫端可觀察的路徑、分支或流程改變時畫；呈現修改後的設計路徑，不標問題。
  - 改動地圖：影響多個模組或層級時畫；標出新增、修改與沒改但受影響的節點，審查後的問題主要標在這張。
  - 關鍵行為：狀態、生命週期或跨元件時序是理解重點時畫；狀態用 `flowchart TD`（`stateDiagram-v2` 的 note 會被排到離狀態很遠的位置），時序用 `sequenceDiagram`。
- 單張圖約 11 個節點為上限；超過時拆成「改了什麼」與「風險在哪」兩張，或把次要節點併入群組表。
- 簡單修改可不畫圖，在本文寫明原因。

## Good Example

```md
改動特徵：失敗後的使用者路徑改變；跨結帳頁、狀態機與購物車 hook；新增失敗狀態
選圖：圖 1 失敗時的路徑前後對照；圖 2 改動地圖（6 個節點）；圖 3 送出後的狀態（flowchart TD）
```

## Bad Example

```md
改動：修改一個錯誤訊息字串
選圖：圖 1、圖 2、圖 3 各一張，圖 2 放 18 個節點
```

# Rule 6 - 版面避免交錯與重疊

- Level: `SHOULD`
- 節點以功能或責任命名，只保留理解改動所需的內容；程式碼名稱有助定位時可直接使用。
- 修改前後放同一張圖時，用 `flowchart TB` 包 `b_`、`a_` 兩個 subgraph（內部 `direction LR`），並以 `b_ ~~~ a_` 連接兩個 subgraph 固定修改前在上；不要用節點跨 subgraph 相連，否則 subgraph 內的 `direction LR` 會失效、變成上下排列。前後節點用不同 id。
- 避免自我迴圈；回流線不加標籤或只用兩三個字的短標籤，同一節點不要接多條帶標籤的回流線。
- 箭頭依圖型表達關係、流程條件、觸發事件或訊息動作；圖下用一兩句說明重要差異。

## Good Example

```md
flowchart TB
  subgraph b_["修改前"]
    direction LR
    b_submit["送出訂單"] -->|失敗| b_clear["清空購物車（移除）"]
  end
  subgraph a_["修改後"]
    direction LR
    a_submit["送出訂單"] -->|失敗| a_error["失敗頁：保留購物車"]
    a_error -->|重試| a_retry["以原購物車再次送出"]
  end
  b_ ~~~ a_
```

## Bad Example

```md
flowchart LR
  submit["送出訂單"] -->|失敗時若錯誤是網路或付款被拒就保留購物車| submit
  error["失敗"] -->|使用者點擊重試按鈕後重新送出同一份購物車| submit
  error -->|使用者選擇返回修改購物車內容| edit["編輯"]
  timeout["逾時"] -->|逾時後清空購物車並回到編輯中| edit
```

# Rule 7 - 底色表示改動類型，框線表示問題等級

- Level: `MUST`
- 底色＝改動類型：綠＝新增、黃＝修改、藍＝沒改但受影響、灰＝移除（標籤加「（移除）」）；沒改也不受影響的節點用 `default` 中性色。
- 框線＝問題等級，只在審查後加上：紅色粗框＝有 P0–P2；灰色虛框＝只有 P3。
- 底色與框線的每種組合各自定義一個 class（例如 `changedMajor`、`affectedMinor`），不依賴多個 class 疊加；顏色照下方定義，只保留用到的行。圖中有 subgraph 時，第一行加 init 設定，把 subgraph 底色改成白色，避免被看成「修改」。
- 問題寫進受影響的節點標籤：P0–P2 寫 `⚠ P<等級> <一句話>（F<編號>）`，P3 寫 `· P3 <一句話>（F<編號>）`；不另拉「問題節點」連到別處。和圖上節點無關的問題（例如註解、未使用的 key）在圖說交代數量。
- 圖下附一行圖例；有藍底紅框時，圖說點名這些節點，說明這次沒改、但前提被破壞的原因。

## Good Example

```md
%%{init: {"themeVariables": {"clusterBkg": "#ffffff", "clusterBorder": "#cbd5e1"}}}%%
classDef default fill:#f8fafc,stroke:#94a3b8,color:#111
classDef added fill:#dcfce7,stroke:#15803d,color:#111
classDef changed fill:#fef3c7,stroke:#b45309,color:#111
classDef affected fill:#e0f2fe,stroke:#0369a1,color:#111
classDef removed fill:#f3f4f6,stroke:#9ca3af,color:#6b7280
classDef addedMajor fill:#dcfce7,stroke:#dc2626,stroke-width:3px,color:#111
classDef changedMajor fill:#fef3c7,stroke:#dc2626,stroke-width:3px,color:#111
classDef affectedMajor fill:#e0f2fe,stroke:#dc2626,stroke-width:3px,color:#111
classDef addedMinor fill:#dcfce7,stroke:#6b7280,stroke-width:2px,stroke-dasharray:5 3,color:#111
classDef changedMinor fill:#fef3c7,stroke:#6b7280,stroke-width:2px,stroke-dasharray:5 3,color:#111
classDef affectedMinor fill:#e0f2fe,stroke:#6b7280,stroke-width:2px,stroke-dasharray:5 3,color:#111

api["訂單 API（未改）<br/>重試時再被呼叫一次<br/>⚠ P0 待驗證：可能重複扣款（F1）"]
class api affectedMajor
圖說：訂單 API 這次沒改，但新增的重試讓同一份購物車可能送出兩次，原本「一次送出只建立一筆訂單」的前提不再成立。
```

## Bad Example

```md
machine["結帳狀態機"]
issue1["P1：逾時仍清空購物車"]
issue1 -.-> machine
class machine changed
class machine major
```

# Rule 8 - 圖中的變更、影響與問題必須可查證

- Level: `MUST`
- 新增、修改、移除的標記對應 diff 中的 hunk；沒改但受影響的標記對應已讀過的呼叫端或依賴關係，並在詳細檔寫明影響原因與位置；因 finding 新增或改標為受影響的節點，以該 finding 的證據為準。
- 問題的框線與標籤對應詳細檔中同編號的 finding，等級一致；finding 改級、合併或排除時，同步修改圖。
- 關係、轉移與訊息有程式碼依據；未證實者在圖說標【推測】，`flowchart` 也可用虛線輔助區分。`sequenceDiagram` 的 `-->>` 是虛線訊息箭頭，本身不表示推測。
- 分支與觸發條件依實際判斷式描述；進入方式會改變離開條件時，用條件標籤或圖說交代差異。

## Good Example

```md
圖 2 `orderSummary`（藍）：詳細檔寫「未修改，但讀取 `useCart().items`，失敗後 items 不再清空【程式碼證實】[Summary.tsx#L12](https://github.com/acme/shop-web/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/checkout/Summary.tsx#L12)」
圖 2 `machine` 紅框「⚠ P1 逾時仍清空購物車（F2）」：詳細檔的 F2 同為 P1
```

## Bad Example

```md
`affected`：訂單摘要、會員中心、推薦商品（可能都會受影響）
圖上仍標「⚠ P1（F2）」，但 F2 已在統整時降為 P2
```

# Rule 9 - 圖改完必須實際渲染確認

- Level: `MUST`
- 每次新增或修改圖後，執行渲染檢查腳本 `render_mermaid.py --report <報告>`，exit code 0 才算通過：
  - 語法錯誤或偵測到重疊（exit code 1）：依 Rule 6 調整版面後重跑。
  - 通過後逐張檢視截圖，確認沒有連線穿過節點、標籤離連線太遠或版面過擠等腳本偵測不到的問題。
  - 節點數超過上限的提醒，依 Rule 5 拆圖，或在圖說交代保留原因。
  - 找不到瀏覽器或無法載入 Mermaid（exit code 3）：不阻擋流程，在詳細檔「比較範圍」的備註寫「圖未經渲染驗證」與原因。

## Good Example

```md
第一次：exit 1，圖 3「返回修改」與「重試」兩個回流標籤重疊 → 拿掉「返回修改」的標籤
第二次：exit 0；檢視 3 張截圖，沒有連線穿過節點
```

## Bad Example

```md
Mermaid 語法看起來沒問題，直接交付。
```
