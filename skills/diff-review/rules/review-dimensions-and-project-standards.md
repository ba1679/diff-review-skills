# Rule 1 - 審查前必須探索受審 repo 自身的規範來源

- Level: `MUST`
- 依下列順序探索，存在才讀；讀取一律針對 head SHA（例如 `git show <head SHA>:AGENTS.md`）：
  1. Agent 指示檔：repo 根目錄與改動檔案所在目錄往上的 `AGENTS.md`、`CLAUDE.md`（含其中以 `@` 匯入的檔案）、`GEMINI.md`、`.github/copilot-instructions.md`。
  2. 貢獻與慣例文件：`CONTRIBUTING.md`、`docs/` 下的 conventions、guidelines、ADR、`.github/pull_request_template.md`、README 中的開發慣例章節。
  3. 編輯器規則：`.cursor/rules/*.mdc`、`.windsurfrules`、`.editorconfig`。
  4. repo 內的 skills：`.claude/skills/*/SKILL.md`、`.agents/skills/*/SKILL.md` 中，description 提到 coding standard、review、conventions、guidelines、a11y、testing 且與本次 diff 相關者。
  5. 工具設定：ESLint、Prettier、TypeScript、Stylelint、Ruff 等設定檔，只用來判斷哪些規則已由工具強制。
- 讀取 repo 內的 skill 時只取其規範內容，不執行其流程：不寫它的 log、不跑它的 gate、不在 PR 留言、不修改檔案。
- 記錄實際讀取的規範來源，寫入報告「已檢查維度」的已讀規範；只探索到、沒有逐條比對的來源要分開列出。
- 找不到任何規範時，仍以本 skill 的通用基準審查，並在報告註明「未找到 repo 規範，僅依通用基準」。

## Good Example

- 這個例子是好的，因為它依序探索並記錄實際讀到的來源，且只取 skill 的規範內容。

```md
已讀規範（head a1b2c3d）：
- AGENTS.md（根目錄）；src/checkout/AGENTS.md（較近，優先）
- .cursor/rules/a11y.mdc
- .claude/skills/frontend-standards/SKILL.md（只取審查維度，未執行其 gate）
- .eslintrc.cjs：react-hooks/exhaustive-deps 為 error，相關問題不重複提
```

## Bad Example

- 這個例子是壞的，因為它沒有探索 repo 規範就用個人偏好審查，也沒有記錄依據。

```md
依一般最佳實踐審查，以下是建議……
```

# Rule 2 - repo 規範優先於通用基準，引用時寫出條目

- Level: `MUST`
- 優先序：repo 明文規範 > 本 skill 通用基準；離改動檔案越近的規範 > 越遠的規範；明確條目 > 一般原則。
- repo 規範明確認可的寫法，即使通用基準會標記，也不提出。
- 已由 lint、型別檢查或 formatter 強制的項目不重複提出；除非規則被停用且沒有說明理由。
- 引用 repo 規範時必須寫出檔案、條目，並引用原文一句；不可只寫「違反專案規範」。
- 規範之間互相衝突時，以進版控、團隊層級的文件為準，並把衝突列入「待確認」。

## Good Example

- 這個例子是好的，因為它引用了具體條目與原文。

```md
依據：AGENTS.md「Coding Style」——"use the `@/` alias for imports so paths stay shallow"
本次新增 `../../../utils/format` 的相對路徑匯入。
```

## Bad Example

- 這個例子是壞的，因為它只說違反規範，讀者無法查證是哪一條。

```md
匯入路徑不符合專案規範，請修正。
```

# Rule 3 - 每次審查都必須涵蓋五個核心維度

- Level: `MUST`
- 正確性：
  - 邊界條件：null 或 undefined、空陣列、0 與負數、極大值、重複項、排序、時區、編碼、權限不足。
  - 錯誤處理：失敗路徑是否處理、錯誤是否被吞掉、使用者是否看得到、是否需要重試或回滾。
  - 非同步競態：過期回應覆蓋新狀態、卸載後更新狀態、重複送出、並行請求的完成順序、取消與逾時。
  - 狀態轉移：每個狀態都能抵達與離開、重設時機、衍生狀態與來源一致、狀態與畫面對應。
- 需求符合度：
  - 對照驗收條件逐條判定：已實作、部分實作、遺漏、矛盾。
  - 找出需求沒有授權的額外行為。
  - 落差分三類並寫明是哪一類：規格沒授權（實作做了規格不允許的事）、規格缺漏（規格沒定義此情境）、實作偏離規格（規格寫了卻沒照做）。
  - 比較範圍只是 ticket 的切片（例如只審部分 commit）時，只判斷「有沒有做錯」，完整性標為未驗證；範圍是完整 PR 或分支時才判斷遺漏。
  - 沒有需求來源時，此維度標為未驗證，不可宣稱符合。
- 專案規範：
  - 依探索到的規範逐條比對，包含命名、目錄結構、匯入方式、樣式 token、i18n、錯誤處理慣例。
  - 測試慣例：變更的行為是否有對應測試、bug fix 是否有回歸測試、測試名稱是否與實際斷言相符、fixture 是否符合真實型別。
- 複用與 DRY：
  - 新增元件、hook、util 或型別時，以 `git grep` 在 head SHA 搜尋既有同名或同功能的實作（本次納入未提交改動時，head 端改在工作目錄搜尋與閱讀（例如 `git grep -n --untracked <pattern>`），引用依 evidence 規則的工作目錄指紋格式）；已有可用的實作卻另寫一份且沒有理由，才列為問題。
  - 相似的程式碼只有在承載同一條規則（同一業務規則、會因同一原因一起修改）時，才建議合併；只是長得像、修改理由不同時，不要求抽象化。
  - 過早抽象也是問題：只有一個使用點的共用層、為假想需求加的參數或擴充點。
- 維護性與單一職責：
  - 責任是否清楚：一個模組或元件能否用一句話說清楚職責。
  - 耦合：是否直接讀寫其他模組的內部狀態、依賴方向是否反轉（例如資料層依賴 UI）。
  - 修改理由：同一模組是否因多個不相關的原因被修改；一個邏輯改動是否被迫分散修改多處。
  - 第二份事實來源：是否新增了與既有狀態或設定重複、日後會不同步的資料。
  - 可讀性：命名、巢狀條件、魔術數字只在影響理解或正確性時提出。

## Good Example

- 這個例子是好的，因為 DRY 的判斷建立在「是否承載同一條規則」上，而不是外觀相似。

```md
複用與 DRY：
- 新增 `formatPrice` → git grep 找到既有 `src/utils/currency.ts#formatCurrency`，同樣依 locale 格式化金額且修改理由相同 → 建議改用既有實作
- `OrderCard` 與 `CartItem` 版面相似，但前者跟訂單狀態變動、後者跟購物車規則變動 → 不要求合併
```

## Bad Example

- 這個例子是壞的，因為它機械地要求抽象化，也沒有檢查其他核心維度。

```md
OrderCard 和 CartItem 有重複的 JSX，應該抽成共用元件。其他看起來沒問題。
```

# Rule 4 - 依改動內容觸發條件維度

- Level: `MUST`
- 下列條件維度只在觸發時檢查，並在報告寫出觸發原因：
  - a11y：改動含 JSX、HTML、樣式或互動行為 → 語意元素、可用鍵盤操作、焦點管理（dialog 的 focus trap 與還原、menu 開關後的焦點去向）、label 與 aria 屬性、顏色對比、動態內容的 live region、標題層級。
  - 安全性：改動涉及使用者輸入、HTML 注入、URL 或 redirect、storage、身分驗證與權限、環境變數或金鑰、檔案上傳、第三方 script → XSS（`dangerouslySetInnerHTML`、`innerHTML`、`javascript:` URL）、open redirect、敏感資料寫入 log、storage 或 URL、權限只在前端檢查、硬編碼金鑰、新增依賴的來源。
  - 效能：改動涉及列表、大量資料、render 熱點、迴圈內請求、新依賴、輪詢或計時器 → 不必要的重新渲染、N+1 請求、未分頁、未清除的 listener 或 timer 造成的記憶體洩漏、大型依賴整包匯入。只在有實際成本時提出。
  - 外部契約：改動涉及 API 呼叫或型別、元件 props、事件 payload、URL 參數、storage schema、i18n key、test id、無障礙角色與名稱、公開函式 → 向後相容、所有消費端（包含依賴角色與名稱定位的測試）是否已同步更新、型別與實際資料形狀是否一致、錯誤碼處理。
  - 資料完整性：改動涉及寫入、刪除或遷移資料 → 不可逆操作是否有確認、部分失敗的處理、重複執行是否冪等。
- 改動含 React 元件或 hook 時，React 慣例由另一份規則承接，不在此重述。

## Good Example

- 這個例子是好的，因為它寫出觸發原因，只檢查被觸發的維度。

```md
條件維度：
- a11y（觸發：新增重試按鈕與錯誤提示）→ 檢查按鈕 label、錯誤訊息 live region
- 外部契約（觸發：`useCart` 回傳形狀改變）→ 檢查所有消費端與測試 mock
- 安全性、效能、資料完整性：未觸發
```

## Bad Example

- 這個例子是壞的，因為它對所有改動套用全部維度，產生與本次改動無關的雜訊。

```md
效能：建議全站導入虛擬列表。安全性：建議加上 CSP。a11y：建議全面檢查對比。
```

# Rule 5 - 工具結果只是佐證，必須揭露實際執行與未執行的檢查

- Level: `MUST`
- 工具的分數、警告數量或「通過」不等於審查結論；每個工具發現仍要經過 finding 判定。
- 只在工具結果能代表 head 時執行會掃描工作目錄的工具：目前 checkout 等於 head SHA 且沒有未提交改動（或本次已納入未提交改動）。否則標示「未執行：工作目錄不是 head」。
- 只對 diff 內的檔案或改動行執行針對性檢查，例如對變更檔執行 ESLint、以 `--scope lines` 執行 React Doctor、型別檢查只計入 diff 內檔案的錯誤；除非使用者要求，不整包重跑測試或全庫 lint。
- 工具需要下載或安裝（例如 `npx <package>@latest`）時，先徵得使用者同意。
- 只使用不寫入受審 repo 的選項，例如 `tsc --noEmit --incremental false`、`eslint --no-cache`；不可使用 `--fix`、`-u` 或任何會更新快照、快取、報告目錄的選項。執行前後以 `git --no-optional-locks status --porcelain --ignored` 比對（含被忽略的快取檔），有新增或修改的檔案時必須揭露。
- 工具比較的範圍可能和本次範圍不同（例如以目前分支對預設分支比較），採用前要先對照範圍。
- 只把本次引入或本次惡化的問題列為 findings；既有問題最多列在「既有問題（非本次引入）」備註，不排序、不計入建議修正。
- PR 模式可讀取 CI 狀態（例如 `gh pr checks`）作為佐證，並寫明執行的指令與 CI 針對的 commit；失敗項目未查看 log 時，原因寫「未驗證」，不可推定與程式碼無關。PR 留言中的品質指標若是相對其他基準（例如相對 main），不可歸因於本次 diff。
- 列出實際執行的檢查、指令與結果；未執行的檢查寫「未執行」與原因，不可寫成通過。

## Good Example

- 這個例子是好的，因為它揭露工具的代表性限制，並區分本次引入與既有問題。

```md
| 檢查 | 結果 | 備註 |
| --- | --- | --- |
| ESLint（5 個變更檔） | 1 個 error | `CheckoutPage.tsx:30` 為本次引入，已列入 P2 |
| React Doctor | 未執行 | 目前 checkout 是 main，不是 head a1b2c3d |
| CI（gh pr checks） | 全部通過 | 針對 head a1b2c3d |
既有問題（非本次引入）：`cartSlice.ts` 有 2 個既有 any，未列入建議修正。
```

## Bad Example

- 這個例子是壞的，因為它把工具分數當成結論，也沒有說明工具掃描的是哪個版本。

```md
React Doctor 分數 92，程式碼品質良好，審查通過。
```
