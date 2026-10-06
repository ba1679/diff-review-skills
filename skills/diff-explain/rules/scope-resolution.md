# Rule 1 - 把使用者輸入轉成腳本 flag，角色判不出來就問

- Level: `MUST`
- Phase 1 READ 的工作是把使用者輸入轉成 `resolve_diff_scope.py` 的 flag：有 PR URL 就帶 `--pr`，使用者明確給的 ref 才帶 `--base` / `--head`（branch、tag、commit SHA、遠端 ref 皆可，原樣傳入，不替使用者改寫）。
- 使用者沒給的部分不要自行推算；下列一律由腳本固定、不在這裡重做：PR 實際回報的 base / head commit、PR 與自訂範圍並存時的優先序、單側 ref 另一側的補齊、預設 `origin/main`、目前分支、detached HEAD，以及各側來源標示。
- 需要你判斷的只有 base / head 的角色：
  - 使用者以 `A -> B`、「從 A 到 B」、「A 和 B 的差異」描述時，A 為 base、B 為 head；語意明確相反（例如「A 相對於 B 改了什麼」）時以語意為準。
  - 只提供單一 ref 時，「since X」「從 X 之後」「X 以來」把 X 當 base；「review X」「看 X 分支」「看懂 X」「解釋 X」把 X 當 head。
  - 不在上述語意內（例如「整理 X」「分析 X」）或角色無法判斷時，先詢問使用者，不可自行假設。

## Good Example

- 這個例子是好的，因為它只把能確定的角色轉成 flag，其餘交給腳本，不替腳本重算。

```md
輸入：https://github.com/acme/web/pull/42 ，請比較 v2.3.0 -> feature/login
解讀：帶 --pr <URL> --base v2.3.0 --head feature/login（A -> B：A 為 base、B 為 head；PR 的優先序由腳本處理）

輸入：幫我 review feature/search
解讀：帶 --head feature/search（「review X」把 X 當 head；base 預設交給腳本）
```

## Bad Example

- 這個例子是壞的，因為單一 ref 的角色語意不明，卻沒有詢問就逕自猜了一邊。

```md
輸入：幫我分析 release/3.2
解讀：「分析」不在 base / head 的語意內，仍直接當成 head 繼續。
```

# Rule 2 - 比較方式與未提交改動維持預設，只依使用者明確要求切換

- Level: `MUST`
- 預設不帶 `--mode` 與 `--include-uncommitted`，也就是以 merge-base 比較、不納入未提交改動。
- 使用者明確要求「兩個版本的完整差異」「直接比較兩版」時才帶 `--mode direct`；明確要求「包含未提交的改動」「我還沒 commit」時才帶 `--include-uncommitted`。
- 不可因為 diff 看起來太少、太多，或偵測到工作目錄有改動，就自行切換。

## Good Example

- 這個例子是好的，因為它只在使用者明確要求時才切換 flag。

```md
輸入：我要 release/3.1 和 release/3.2 兩個版本的完整差異
解讀：帶 --base release/3.1 --head release/3.2 --mode direct

輸入：幫我看目前的改動，我還沒 commit
解讀：帶 --include-uncommitted
```

## Bad Example

- 這個例子是壞的，因為使用者沒有要求，卻依 diff 結果或工作目錄狀態自行切換。

```md
merge-base 模式只有 3 個檔案，看起來不完整，改用 --mode direct 重跑。
偵測到工作目錄有改動，為了完整一併帶 --include-uncommitted。
```

# Rule 3 - 腳本報錯或有 warnings 時停下來交給使用者，不可自行換範圍

- Level: `MUST`
- 腳本失敗時，轉述它的錯誤與提示後停止；可以附上以唯讀指令查到的原因或可選的 ref 供使用者選擇，但不可自行採用，也不可換 base、改審工作目錄或另一個 PR 後重跑。
- `run.json` 的 `warnings` 不為空時，先向使用者顯示並取得確認，才進入 Phase 2。
- `run.json` 的 `notes` 全部寫入範圍顯示的「備註」。

## Good Example

- 這個例子是好的，因為它把報錯與 warnings 都當成停點，附上查到的原因與選項，但交給使用者決定。

```md
無法固定比較範圍：找不到 `origin/main`。
經查此 repo 的 origin/HEAD 指向 `origin/develop`。請指定 base，例如「base=origin/develop」，我再繼續。

比較範圍已固定，但有一項警告：固定範圍的檔案清單與 GitHub PR 不一致，可能是 PR 在讀取後有新 push。
要以目前固定的 head（a1b2c3d4e5f6）繼續，還是重新讀取 PR？
```

## Bad Example

- 這個例子是壞的，因為它自行換了 base，也把 warnings 藏進備註後直接開始分析。

```md
origin/main 不存在，改用 origin/develop 繼續分析。
備註：檔案清單有些不一致。（直接開始分析）
```

# Rule 4 - 不改動受審 repo 的工作目錄

- Level: `MUST`
- 不可執行 checkout、switch、reset、stash、clean、commit、rebase、merge，也不可在受審 repo 的工作目錄內新增或修改任何檔案（包含暫存檔與報告草稿）。
- 目前 checkout 不是 head 時，以 `git show <sha>:<path>` 等固定 SHA 方式讀取，不切換分支。

## Good Example

- 這個例子是好的，因為 head 沒有 checkout 時，它仍以固定 SHA 讀取，沒有動到工作目錄。

```md
目前 checkout：main，head：feature/cart（a1b2c3d4e5f6）
讀取 head 版本：git show a1b2c3d4e5f6:src/cart/useCart.ts
```

## Bad Example

- 這個例子是壞的，因為它為了方便閱讀切換分支，改動了使用者的工作目錄。

```md
git stash && git checkout feature/cart
讀完後再 git checkout main && git stash pop
```
