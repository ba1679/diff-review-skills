# Rule 1 - 依固定優先序解讀 base 與 head

- Level: `MUST`
- 同時提供 PR URL 與自訂 base / head 時，自訂範圍優先；PR 只作為需求與背景來源，不決定比較範圍。
- 只提供 PR URL 時，使用 PR 實際回報的 base 與 head commit（例如 `gh pr view` 的 `baseRefOid`、`headRefOid`），不可用 branch 名稱自行推算；PR 的 base 不是預設分支（疊在其他 PR 上）時，仍以 PR 的 base 為準。
- 明確提供 base / head 時，接受 branch、tag、commit SHA 與遠端 ref（例如 `origin/feature-x`）。
- 只提供一個 ref 時，依語意判斷：「since X」「從 X 之後」「X 以來」把 X 當 base、head 為目前分支；「review X」「看 X 分支」把 X 當 head、base 為預設值；語意無法判斷時先詢問使用者，不可自行假設。
- 同時提供 PR URL 與單側 ref 時，使用者給的一側以使用者為準，另一側用 PR 回報的 commit 補齊，並在範圍顯示中標示各自來源。
- 完全未指定時，base 為 `origin/main`，head 為目前分支；目前處於 detached HEAD 時，head 為 `HEAD` 並在範圍顯示中標示。
- 使用者以 `A -> B`、「從 A 到 B」、「A 和 B 的差異」描述時，一律 A 為 base、B 為 head；使用者語意明確相反時（例如「A 相對於 B 改了什麼」），以語意為準並在範圍顯示中寫出對應結果。

## Good Example

- 這個例子是好的，因為它在 PR 與自訂範圍並存時讓自訂範圍決定 diff，也依語意判斷單一 ref 的角色。

```md
輸入：https://github.com/acme/web/pull/42 ，請比較 v2.3.0 -> feature/login
解讀：
- base = v2.3.0，head = feature/login（自訂範圍優先）
- PR #42：只讀取描述、連結 issue 與討論，作為需求來源

輸入：幫我 review feature/search
解讀：head = feature/search，base = origin/main（「review X」把 X 當 head）
```

## Bad Example

- 這個例子是壞的，因為它用 PR 的 branch 名稱自行推算範圍，遇到疊在其他 PR 上的 PR 會把別人的改動算進來。

```md
輸入：https://github.com/acme/web/pull/42
解讀：PR head 是 feature/login，所以比較 origin/main...origin/feature/login
```

# Rule 2 - 預設以 merge-base 比較，只有明確要求才改為兩點直接比較

- Level: `MUST`
- 預設使用 `git diff <base>...<head>`，比較 merge-base 到 head 的改動，也就是 head 這一側實際帶來的改動。
- 只有使用者明確要求「兩個版本的完整差異」「直接比較兩版」「A 與 B 全部差在哪」時，才改用 `git diff <base> <head>`。
- 不可因為某種模式的 diff 比較小、比較大或比較好讀而自行切換。
- 採用兩點直接比較時，範圍顯示必須說明：結果也會包含 base 之後才出現、head 沒有的改動（以反向差異呈現）。

## Good Example

- 這個例子是好的，因為它只在使用者明確要求完整差異時切換模式，並說明影響。

```md
輸入：我要 release/3.1 和 release/3.2 兩個版本的完整差異
解讀：比較方式 = 兩點直接比較 `git diff release/3.1 release/3.2`
說明：結果包含兩邊各自的改動，不只是 3.2 新增的部分
```

## Bad Example

- 這個例子是壞的，因為使用者沒有要求，卻因 merge-base 結果「太少」而改用兩點比較。

```md
merge-base 模式只有 3 個檔案，看起來不完整，改用 git diff main feature-x 比較完整。
```

# Rule 3 - 未提交改動預設不納入，只有明確要求才納入

- Level: `MUST`
- 預設不包含 staged、unstaged 與 untracked 改動。
- 只有使用者明確要求（例如「包含未提交的改動」「我還沒 commit」「連 working tree 一起看」）才納入。
- 納入時 head 必須是目前 checkout 的分支；head 指向其他 ref 時，停止並說明未提交改動只存在於目前工作目錄。
- 納入時 head 標示為「HEAD 加未提交改動」，因為這部分沒有 SHA 可固定，必須記錄指紋並提醒使用者審查期間不要修改工作目錄。
- 未納入、目前 checkout 等於 head，且工作目錄有未提交改動時，範圍顯示必須寫出「未納入 N 個未提交檔案」，避免使用者誤以為已被審查。

## Good Example

- 這個例子是好的，因為它沒有被要求就不納入，並主動揭露被排除的內容。

```md
比較範圍：origin/main...feature/cart（a1b2c3d4e5f6）
未提交改動：未包含（工作目錄另有 3 個未提交檔案，本次未審查）
```

## Bad Example

- 這個例子是壞的，因為它在使用者沒有要求時，自行把工作目錄改動混進審查範圍。

```md
偵測到工作目錄有改動，為了完整一併納入審查。
```

# Rule 4 - 範圍無法成立時說明原因並停止，不可靜默替換

- Level: `MUST`
- 下列情況必須向使用者說明原因與可行的修正方式後停止：PR 無法存取（`gh` 未安裝、未登入、無權限、PR 不存在）、PR 不屬於目前 repo、ref 不存在、預設的 `origin/main` 不存在、diff 為空。
- 可行修正方式要具體，例如執行 `git fetch origin`、`gh auth login`、確認 URL，或請使用者指定 base（`origin/main` 不存在時，可列出 `origin/HEAD` 指向的分支供使用者選擇，但不可自行採用）。
- 不可靜默改用其他 base、改審工作目錄 diff、改審另一個 PR，或把空 diff 當成「沒有問題」。

## Good Example

- 這個例子是好的，因為它說明失敗原因與修正方式，並停在範圍確認之前。

```md
無法固定比較範圍：找不到 `origin/main`。
這個 repo 的預設分支看起來是 `origin/develop`（來自 origin/HEAD）。
請指定 base，例如「base=origin/develop」，我再繼續。
```

## Bad Example

- 這個例子是壞的，因為它在預設 base 不存在時自行換成另一個分支繼續，使用者不會知道範圍變了。

```md
origin/main 不存在，改用 origin/develop 繼續分析。
```

# Rule 5 - 只讀取受審 repo，不為了 review 改動工作目錄

- Level: `MUST`
- 不可執行 checkout、switch、reset、stash、clean、commit、rebase、merge，也不可修改受審 repo 的任何檔案。
- 允許讀取 git 物件，也允許以 `git fetch` 取得缺少的 PR commit 或遠端 ref；fetch 只更新 remote-tracking ref，不動工作目錄，且必須在範圍顯示中揭露。
- 讀程式碼一律使用固定 SHA，例如 `git show <sha>:<path>`、`git grep <pattern> <sha>`；只有 checkout 等於 head SHA 且沒有未提交改動時，才可直接讀工作目錄檔案。
- 本次納入未提交改動時，head 端的內容只存在於工作目錄：被修改或新增的檔案改讀工作目錄，以 `diff.patch` 為權威 diff；base 端與未修改的檔案仍以固定 SHA 讀取。審查期間若發現工作目錄與 `diff.patch` 不一致，必須揭露，不可默默改用新內容。
- 執行目錄、報告草稿與任何暫存檔都放在受審 repo 之外。

## Good Example

- 這個例子是好的，因為它在 head 沒有 checkout 時，仍從固定 SHA 讀到正確內容。

```md
目前 checkout：main（9f8e7d6c5b4a），head：feature/cart（a1b2c3d4e5f6）
讀取 head 版本：git show a1b2c3d4e5f6:src/cart/useCart.ts
讀取修改前版本：git show <merge-base SHA>:src/cart/useCart.ts
```

## Bad Example

- 這個例子是壞的，因為它為了方便閱讀切換分支，改動了使用者的工作目錄。

```md
git stash && git checkout feature/cart
讀完後再 git checkout main && git stash pop
```

# Rule 6 - 範圍顯示必須揭露 notes，遇到 warnings 先取得使用者確認

- Level: `MUST`
- 顯示比較範圍時，`run.json` 的 `notes` 必須全部寫入「備註」，包含：執行過的 `fetch`、兩點比較時 base 端多出的 commit、目前 checkout 不是 head、未產生 permalink 的原因、未審查的未提交檔案數。
- `run.json` 的 `warnings` 不為空時（例如固定範圍的檔案清單與 GitHub PR 不一致），先向使用者顯示 warnings 並取得確認，才進入後續分析。
- `pr.role` 為 `partial` 或 `context` 時，範圍顯示必須寫出哪一側來自使用者、哪一側來自 PR。

## Good Example

- 這個例子是好的，因為它把 warnings 當成停點，而不是附註後繼續。

```md
比較範圍已固定，但有一項警告需要確認：
- 固定範圍的檔案清單與 GitHub PR 不一致：僅 GitHub ["src/a.ts"]，可能是 PR 在讀取後有新 push。
要以目前固定的 head（a1b2c3d4e5f6）繼續，還是重新讀取 PR？
```

## Bad Example

- 這個例子是壞的，因為它把會影響範圍正確性的警告藏在備註裡，直接開始分析。

```md
備註：檔案清單有些不一致。
（直接開始分析）
```
