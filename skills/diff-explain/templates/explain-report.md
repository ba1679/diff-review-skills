# {{REPORT_KIND}}：{{CHANGE_TITLE}}

**{{REPORT_STATUS}}**｜`{{BASE_REF}}` ← `{{HEAD_REF}}`（`{{HEAD_SHA_SHORT}}`）｜{{FILE_COUNT}} 檔 +{{ADDITIONS}}／−{{DELETIONS}}

## 一句話

{{ONE_LINE_SUMMARY}}

<!-- 依規則選圖：用不到的圖連同標題刪除，保留的圖依序編號；完全不畫圖時只保留下一行，並刪除所有圖的區塊；畫圖時刪除下一行 -->
本次不繪圖：{{NO_DIAGRAM_REASON}}

## 圖 1：{{BEFORE_AFTER_TITLE}}

```mermaid
%%{init: {"themeVariables": {"clusterBkg": "#ffffff", "clusterBorder": "#cbd5e1"}}}%%
flowchart TB
  subgraph b_["修改前"]
    direction LR
    {{BEFORE_FLOW}}
  end
  subgraph a_["修改後"]
    direction LR
    {{AFTER_FLOW}}
  end
  b_ ~~~ a_
  {{BEFORE_AFTER_CLASS_DEFINITIONS}}
```

{{BEFORE_AFTER_CAPTION}}

## 圖 2：改動地圖

```mermaid
flowchart LR
  {{CHANGE_MAP}}
  {{CHANGE_MAP_CLASS_DEFINITIONS}}
```

{{CHANGE_MAP_CAPTION}}

## 圖 3：{{KEY_BEHAVIOR_TITLE}}

```mermaid
{{KEY_BEHAVIOR_DIAGRAM}}
```

{{KEY_BEHAVIOR_CAPTION}}

## 改動群組

| 群組 | 類型 | 改了什麼 |
| --- | --- | --- |
| {{GROUP_NAME}} | {{GROUP_TYPE}} | {{GROUP_CHANGE}} |

> 比較範圍與逐項證據在 `{{DETAIL_FILE}}`，需要追查時再看。
