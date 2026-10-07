<!-- 用 Edit 局部修改 draft.md：取代標題與狀態列 -->
# Code Review：{{CHANGE_TITLE}}

**{{REPORT_STATUS}}**｜`{{BASE_REF}}` ← `{{HEAD_REF}}`（`{{HEAD_SHA_SHORT}}`）｜{{FILE_COUNT}} 檔 +{{ADDITIONS}}／−{{DELETIONS}}｜**P0 {{P0_COUNT}}・P1 {{P1_COUNT}}・P2 {{P2_COUNT}}・P3 {{P3_COUNT}}**｜{{CHECKS_SUMMARY}}

## 一句話

<!-- 保留原本的一句話，在末尾補上問題集中在哪 -->
{{ONE_LINE_SUMMARY}}{{ISSUE_FOCUS}}

<!-- 圖 1～3 沿用 draft.md；依圖表規則把 findings 疊到對應節點（主要是改動地圖與關鍵行為，不標在修改前後對照圖），改動地圖的標題改為「改動地圖＋問題標在節點上」，並更新圖例與圖說 -->

<!-- 「改動群組」沿用 draft.md；以下三節加在它之後、結尾的詳細檔指引之前 -->

## 要處理的問題

<!-- 沒有 finding 時，本節只寫「未發現需修正的問題。」。日後把問題留成 PR 草稿留言時，可把「詳細」改為留言連結；送出 review 前只有本人看得到 -->
| 等級 | 問題 | 建議 | 詳細 |
| --- | --- | --- | --- |
| P{{SEVERITY_LEVEL}} | {{FINDING_SHORT_TITLE}} | {{FIX_SHORT}} | F{{FINDING_NUMBER}} |

## 待確認

<!-- 沒有需要他人回答的問題時刪除本節 -->
- {{OPEN_QUESTION}}

## 驗證範圍

- **跑過**：{{CHECKS_RUN}}
- **沒驗**：{{CHECKS_NOT_RUN}}

> 比較範圍、完整 findings 與審查涵蓋在 `{{DETAIL_FILE}}`，需要追查時再看。
