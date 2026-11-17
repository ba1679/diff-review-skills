# Rule 1 - 先確認受影響套件的環境與指南適用性

- Level: `MUST`
- 本檔適用於 diff 涉及 React／Next.js 程式碼、依賴或設定；也包含會改變其行為的共用資料取得與匯入路徑。非相關改動不載入外部指南，不掃描整個 repo 尋找 React 問題。
- 以固定 head 的受影響套件 `package.json`、lockfile、框架設定及實際匯入判斷 React／Next.js 版本、client／server 邊界與 React Compiler 是否啟用；monorepo 逐套件判斷。納入未提交改動時依證據規則讀取 head 端，不以宿主工作目錄或單一 `.tsx` 副檔名推定環境。
- React 19 專屬規則只在版本與 API 均適用時採用；React 18 或更早跳過 `react19-`。Next.js、RSC／SSR、框架快取及 Compiler 相關建議同樣先核對適用條件。版本或設定未知時，記錄未確認之處，不據此要求升級、遷移或新增依賴。
- 外部指南是補充判準，優先序與 repo 規範的處理沿用 `review-dimensions-and-project-standards.md`；不得把指南的建議升格成 repo 明文規範。

## Good Example

- 按受影響套件判斷版本，不借用其他套件的設定。

```md
packages/legacy-ui 使用 React 18，apps/web 使用 React 19 + Next.js。
本次只改 legacy-ui 的元件 API → 可讀 composition 的 architecture 規則，跳過 react19 與 Next.js 專屬規則。
```

## Bad Example

- 從不適用的環境要求遷移。

```md
repo 有一個 Next.js app，所以所有 React 18 套件都應改用 use() 與 next/dynamic。
```

# Rule 2 - 原始指南保留完整判準，本地只負責按需路由

- Level: `MUST`
- 由派發位置或宿主 skill 清單定位 `vercel-react-best-practices` 與 `vercel-composition-patterns`；未知時只檢查本 skill 的同層安裝目錄。不硬編碼開發者的絕對路徑，不自動安裝或下載來源。
- 初審先讀適用來源的 `SKILL.md` 完整索引，依下表與 diff 選出相關項，再讀其 `rules/` 原始檔全文（含範例、例外與版本條件）。原始檔是單一來源；本表不取代索引中的子項，不複製本地判準副本，也不只憑索引標題產出 finding。不預先讀完整 `AGENTS.md` 或全部 rules。
- 效能來源 `vercel-react-best-practices` 的八類，按原始索引優先順序選讀；所有分類均可觸發，不只限於下表的例子。

| 分類／前綴 | 本次改動的選讀線索 |
| --- | --- |
| 請求瀑布 `async-` | await、請求依賴、條件分支、串流邊界 |
| Bundle `bundle-` | 新依賴、匯入方式、動態路徑、條件載入、第三方 script |
| Server `server-` | API／server action、RSC／SSR、快取、序列化、跨請求狀態 |
| Client 資料取得 `client-` | 重複請求、全域 listener、storage schema |
| 重繪 `rerender-` | state、effect、hook、依賴參照、memo、互動回應 |
| 渲染 `rendering-` | 長列表、SVG、hydration、條件顯示、載入狀態、資源提示 |
| JavaScript `js-` | 熱路徑迴圈、查找、排序、DOM／storage 存取與快取 |
| 進階模式 `advanced-` | 訂閱回呼、初始化時機、最新值參照、Effect Event |

- Composition 來源 `vercel-composition-patterns` 的四類，僅在元件 API、變體、組合邊界或共享狀態改動時選讀。

| 分類／前綴 | 本次改動的選讀線索 |
| --- | --- |
| 元件架構 `architecture-` | boolean 模式組合、compound components、共享 context |
| 狀態管理 `state-` | provider 封裝、state／actions／meta 介面、跨 sibling 共用狀態 |
| 實作模式 `patterns-` | explicit variants、children、render props |
| React 19 API `react19-` | ref 與 context API；必須先符合 Rule 1 的版本條件 |

- 先前本地的衍生 state、互動 effect 與函式式更新判準，分別由來源的 `rerender-derived-state-no-effect`、`rerender-move-effect-to-event`、`rerender-functional-setstate` 承接；diff 涉及該主題時必須選讀對應原始 rule，不保留本地備份。
- 缺少 skill、索引或個別適用 rule 時，記錄具體缺漏與受影響主題；其餘可用的指南與本地審查照常完成。不把未讀項目列為通過，也不把只讀索引寫成全部規則已檢查。

## Good Example

- 保留來源索引的完整選擇空間，再讀實際相關的規則。

```md
diff 在 React 頁面新增兩個 await，並用 effect 同步衍生 state。
讀效能來源索引 → 讀 async-parallel 與 rerender-derived-state-no-effect 原文與範例。
沒有元件 API 或組合邊界改動 → composition 標示未觸發。
```

## Bad Example

- 摘要取代來源或擴大範圍。

```md
只記得「多用 memo、少用 boolean」，未讀原始規則便列問題；順便檢查全站所有元件。
```

# Rule 3 - Finding 仍須有本次引入的具體成本或維護風險

- Level: `MUST`
- 所有候選問題仍須通過 `severity-and-findings.md`，先比對 base／head 與受影響消費端，確認觸發路徑及本次引入或惡化的影響。指南的 `CRITICAL`、`HIGH` 等只是來源優先順序，不能直接映射為 P0–P3。
- 效能候選須指出實際多出的工作或阻塞路徑，例如可獨立的請求變成串行、重複請求、大型模組進入初始 client 路徑、昂貴子樹頻繁重繪。可由程式碼證明結構性成本，不強制每次跑 benchmark；未量測時不可編造毫秒、bundle 大小或受影響人數。依賴 tree-shaking、資料量或執行期行為才能成立者，須補證據或依 finding 規則標示待驗證，不以微小寫法差異湊數。
- Composition 只在具體維護風險時提出：指出非法 props 組合及其後果、同一變體規則散落而必須一起修改的位置、洩漏狀態實作而連帶修改的消費端，或第二份狀態造成不同步的路徑。不能只說「未來不好擴充」。
- boolean props、render props、未使用 provider／compound components、`forwardRef`、`useContext` 或未手動 memo，本身均不足以構成 finding；不因指南偏好就要求換 API、加函式庫或重構整組元件。只提出排除具體風險所需的最小修正。
- 同一根因同時涉及既有 React 慣例、效能與 composition 時，只列一條 finding、可標多個維度；沿用既有去重規則。

## Good Example

- 維護風險指向本次改動中具體會一起修改的規則。

```md
新增 embedded 模式後，Submit 與Toolbar 分別以不同 boolean 組合判定同一個儲存策略。
追讀兩個消費端確認判定已不一致 → 提出一條 finding，列出兩處與最小統一方式。
```

## Bad Example

- 純偏好或虛構量測不能成為 finding。

```md
P1：有兩個 boolean props，所以應改成 compound components。
P1：用了 barrel import，所以首屏一定慢 500ms（未查 bundle 或執行路徑）。
```

# Rule 4 - 以實際採用的來源交接，涵蓋狀態與證據分開記錄

- Level: `MUST`
- 初審的外部來源登記與主 agent 驗收依 `review-agent-handoff.md`；使用既有 `criteria` 陣列，不新增另一套規則清單。實際採用的本檔與外部 rule 必須能由兩位複核者讀取；只讀索引的項目不登記成已採用 rule。
- 依 `templates/review-findings.md` 的外部指南段落，記錄環境依據、每個來源的觸發／未觸發／缺漏狀態、採用的 rule 絕對路徑及內容 SHA-256；版本號可補充，不能取代內容雜湊。初審交付前再確認採用檔案未變動。若有變動，先重讀並重判受影響候選問題，再更新紀錄。
- finding 採用外部指南時，在既有「依據規範」欄位標示「外部指南」及 rule ID／路徑；程式碼與影響證據仍放在證據欄位，不把指南當作問題已成立的證明。
- 外部來源缺漏是涵蓋限制，無 finding 不代表該主題已通過；本地核心審查若完成，仍可交付 completed，但最終報告須保留這項限制。

## Good Example

- 規則與涵蓋紀錄能一一對應。

```md
criteria：本檔與已讀的 async-parallel.md 絕對路徑。
外部指南紀錄：React 版本證據、來源 SKILL.md 位置、該 rule 的 SHA-256、未跑效能量測。
finding：依據規範標「外部指南 async-parallel」；證據另列 base／head 的獨立請求與串行路徑。
```

## Bad Example

- 將來源當作效能證據，或隱藏缺漏。

```md
依據：Vercel 說這是 HIGH，所以本次一定有嚴重效能退化。
來源不存在，但仍寫「已檢查全部 React 最佳實踐」。
```
