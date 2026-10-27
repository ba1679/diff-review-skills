# 詳細證據：{{CHANGE_TITLE}}

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

## 改動證據

| 群組 | 主要位置 | 涵蓋檔案 |
| --- | --- | --- |
| {{GROUP_NAME}} | {{GROUP_MAIN_LOCATION}} | {{GROUP_FILES}} |

<!-- 以下三節沒有內容時連同標題刪除 -->
### 重構一致性

- {{REFACTOR_GROUP_NAME}}：預期一致的行為為 {{EXPECTED_INVARIANTS}}；支持證據：{{INVARIANT_EVIDENCE}}；尚未證實：{{UNVERIFIED_INVARIANTS}}

### 沒改但受影響

- {{AFFECTED_NODE}}：{{AFFECTED_REASON}}{{AFFECTED_EVIDENCE}}

### 推測與資訊缺口

- {{ASSUMPTION}}【推測】依據：{{ASSUMPTION_BASIS}}；驗證方式：{{VERIFICATION_METHOD}}
