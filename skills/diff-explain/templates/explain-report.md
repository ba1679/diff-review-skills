# {{REPORT_KIND}}：{{CHANGE_TITLE}}

> 報告狀態：{{REPORT_STATUS}}

## 比較範圍

| 項目 | 內容 |
| --- | --- |
| Repository | {{REPO_NAME}}（`{{REPO_PATH}}`） |
| Base | `{{BASE_REF}}` → `{{BASE_SHA_SHORT}}`（{{BASE_SOURCE}}） |
| Head | `{{HEAD_REF}}` → `{{HEAD_SHA_SHORT}}`（{{HEAD_SOURCE}}） |
| Merge-base | `{{MERGE_BASE_SHA_SHORT}}` <!-- 兩點比較且沒有共同祖先時寫「（無共同祖先）」 --> |
| 比較方式 | {{COMPARE_MODE}}：`{{DIFF_COMMAND}}` |
| 未提交改動 | {{UNCOMMITTED_STATUS}} |
| 規模 | {{FILE_COUNT}} 個檔案，+{{ADDITIONS}} / -{{DELETIONS}}，{{COMMIT_COUNT}} 個 commit |
| PR | {{PR_ROLE}} |
| 需求來源 | {{REQUIREMENT_SOURCES}} |
| 備註 | {{SCOPE_NOTES}} |

## 1. 改動摘要

**一句話**：{{ONE_LINE_SUMMARY}}

### 改動群組

| 群組 | 類型 | 主要檔案 |
| --- | --- | --- |
| {{GROUP_NAME}} | {{GROUP_TYPE}} | {{GROUP_FILES}} |

<!-- 每個非重構群組各複製一份下列區塊；沒有重構群組時刪除「（重構）」區塊 -->
### {{GROUP_NAME}}（{{GROUP_TYPE}}）

- 目的：{{GROUP_PURPOSE}}
- 必要性：{{GROUP_NECESSITY}}
- 不改的後果：{{GROUP_CONSEQUENCE}}
- 證據：{{GROUP_EVIDENCE}}

### {{REFACTOR_GROUP_NAME}}（重構）

- 目的：{{REFACTOR_PURPOSE}}
- 必要性：{{REFACTOR_NECESSITY}}
- 不改的後果：{{REFACTOR_CONSEQUENCE}}
- 預期一致的行為：{{EXPECTED_INVARIANTS}}
- 支持證據：{{INVARIANT_EVIDENCE}}
- 尚未證實：{{UNVERIFIED_INVARIANTS}}

## 2. 圖解改動

<!-- 依規則不需要畫圖時，只保留下一行並刪除其餘圖表區塊；需要畫圖時刪除下一行 -->
本次不繪圖：{{NO_DIAGRAM_REASON}}

### {{DIAGRAM_TITLE}}

```mermaid
{{MERMAID_DIAGRAM}}
```

圖例：{{DIAGRAM_LEGEND}}

{{DIAGRAM_EXPLANATION}}
