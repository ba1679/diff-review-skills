# Rule 1 - Hooks 必須符合呼叫規則且依賴完整

- Level: `MUST`
- Hooks 只能在元件或自訂 hook 的頂層呼叫，不可放在條件、迴圈、提早 return 之後或巢狀函式內。
- `useEffect`、`useMemo`、`useCallback` 的依賴陣列必須完整；不可為了避免重跑而刻意漏掉依賴，也不可把依賴陣列當成「某個值改變時才執行」的偵測器。
- 自訂 hook 回傳的物件、陣列或函式若每次 render 都是新的參照，而下游把它放進依賴陣列，會造成 effect 重複執行；要確認回傳值的參照穩定性。
- 依賴中出現每次 render 都新建的物件或函式時，先檢查能否移出元件或改為原始值，而不是直接加 `useMemo`。

## Good Example

- 這個例子是好的，因為它找出依賴不穩定的真正來源與後果，而不是只說缺依賴。

```md
`useCheckout` 每次 render 回傳新的 `options` 物件，`CheckoutPage` 的 effect 依賴 `options`
→ 每次 render 都重新呼叫 `fetchShipping()`，造成重複請求【程式碼證實】
```

## Bad Example

- 這個例子是壞的，因為它建議用漏掉依賴的方式「修好」重複執行。

```md
effect 一直重跑，建議把依賴陣列改成 [] 就不會重複呼叫了。
```

# Rule 2 - Effect 只用於與外部系統同步，並要處理競態

- Level: `MUST`
- 可以從 props 或 state 直接算出的值，要在 render 時計算，不可用 effect 同步到另一個 state。
- 回應使用者操作的邏輯（送出、點擊後的導頁、顯示通知）放在 event handler，不放在監聽 state 的 effect。
- 在 effect 中抓取資料時，必須處理競態（忽略過期回應或使用 `AbortController`）、loading 與 error 狀態。
- 不可寫 `useEffect(async () => ...)`；要在 effect 內定義 async 函式再呼叫。
- effect 鏈（effect A 設 state 觸發 effect B）通常代表邏輯應合併到事件處理或計算中。

## Good Example

- 這個例子是好的，因為它指出競態的觸發情境與後果。

```md
切換訂單篩選時，effect 依 `filter` 抓取資料但未忽略過期回應：
快速從「全部」切到「已出貨」，若「全部」的回應較晚回來，畫面會顯示錯誤的清單。
```

## Bad Example

- 這個例子是壞的，因為它用 effect 同步可計算的值，製造了多餘的 render 與不同步風險。

```tsx
const [total, setTotal] = useState(0);
useEffect(() => { setTotal(items.reduce((s, i) => s + i.price, 0)); }, [items]);
```

# Rule 3 - 有副作用的訂閱與計時都必須清理

- Level: `MUST`
- 事件 listener、訂閱、計時器（`setTimeout`、`setInterval`）、observer、WebSocket、`requestAnimationFrame` 都必須在 effect 的 cleanup 中解除。
- 開發模式下 effect 可能被執行兩次（Strict Mode）；effect 必須能安全地重複執行。
- 卸載後的非同步回呼不可再更新狀態或觸發導頁。

## Good Example

- 這個例子是好的，因為它指出缺少清理時的具體後果。

```md
`useAutosave` 以 setInterval 每 5 秒儲存，但 cleanup 未 clearInterval
→ 離開編輯頁後仍持續送出儲存請求，重新進入時會累積多個計時器【程式碼證實】
```

## Bad Example

- 這個例子是壞的，因為它只提出泛泛提醒，沒有指出哪個訂閱缺清理。

```md
請記得 effect 都要有 cleanup。
```

# Rule 4 - 狀態必須維持單一事實來源並放在正確層級

- Level: `MUST`
- 不可把 props 複製進 state（除非刻意作為初始值，並以 `initialX` 之類的名稱表明）；props 改變後 state 不會跟著更新。
- 同一份資料不可同時存在於多個 state 或 store；衍生資料要由來源計算。
- 狀態放在最近的共同祖先；全域 store 只放真正跨頁面共用的資料；伺服器資料與 UI 狀態要分開管理。
- 新狀態依賴前一個狀態時，要用函式形式更新。
- 列表的 `key` 要穩定且唯一；項目會重新排序、插入或刪除時不可用 index 當 key；用 `key` 重設元件狀態時要確認是刻意的。

## Good Example

- 這個例子是好的，因為它指出鏡像 props 造成的具體錯誤。

```md
`AddressForm` 以 `useState(props.address)` 保存地址，切換收件人後 props 改變但表單仍顯示舊地址【程式碼證實】
```

## Bad Example

- 這個例子是壞的，因為它在沒有實際問題時，只因寫法不同就要求改用全域 store。

```md
建議把所有表單狀態移到 Redux，比較好管理。
```

# Rule 5 - 互動行為必須在重複操作、失敗與焦點上保持正確

- Level: `MUST`
- 送出類操作要防止重複點擊或重複送出；`disabled` 與 loading 狀態要一致。
- 表單不可混用受控與非受控；只改 `defaultValue` 不會更新已掛載的輸入框。
- 開關 dialog、menu、popover 時，焦點要有明確去向；Escape、Enter 等鍵盤行為要與滑鼠操作一致。
- 樂觀更新要有失敗回滾，並讓使用者知道失敗。

## Good Example

- 這個例子是好的，因為它說明重複送出的觸發方式與後果。

```md
「下單」按鈕在請求期間仍可點擊（`disabled` 只依表單驗證）
→ 網路慢時連點兩次會建立兩筆訂單【程式碼證實】
```

## Bad Example

- 這個例子是壞的，因為它沒有觸發情境，只是偏好。

```md
按鈕建議加上 loading 動畫會比較好看。
```

# Rule 6 - Memoization 只在有實際成本時要求

- Level: `SHOULD`
- 只有在昂貴計算、昂貴子樹重繪或參照穩定性影響 effect 時，才要求 `useMemo`、`useCallback`、`memo`。
- `memo` 包住的子元件若每次都收到新的物件或函式 props，memo 不會生效；要指出是哪個 props 破壞了它。
- Context 的 value 每次 render 都是新物件時，所有 consumer 都會重繪；只有 consumer 多或重繪昂貴時才提出。
- 依 repo 實際使用的 React 版本判斷建議；不要求未使用的新 API 或遷移。

## Good Example

- 這個例子是好的，因為它指出 memo 失效的原因與實際成本。

```md
`OrderList`（約 500 列）以 memo 包住，但父層每次傳入 `onSelect={() => ...}`
→ memo 失效，每次輸入搜尋字都重繪 500 列
```

## Bad Example

- 這個例子是壞的，因為它在沒有成本的情況下要求到處加 memoization。

```md
所有函式都應該包 useCallback、所有計算都應該包 useMemo。
```

# Rule 7 - React 慣例違反依實際影響決定嚴重性

- Level: `MUST`
- 違反 React 慣例本身不決定嚴重性；依是否造成錯誤行為、競態、資料錯誤或洩漏判定。
- 沒有實際影響的慣例偏離，最多列為低嚴重性或不提出。
- repo 規範或 lint 已明確允許的寫法，不因本規則提出。

## Good Example

- 這個例子是好的，因為嚴重性由實際後果決定。

```md
effect 缺少競態處理：快速切換篩選會顯示錯誤清單，影響主要功能 → 依影響判定
effect 依賴陣列多放了一個穩定的 dispatch：無實際影響 → 不提出
```

## Bad Example

- 這個例子是壞的，因為它只因違反慣例就給高嚴重性。

```md
使用了 index 當 key（列表不會重排）→ 高嚴重性
```
