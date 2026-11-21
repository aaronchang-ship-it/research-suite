# research-suite — 文獻研究與技術報告 skill 套件

Claude Code / Cowork **plugin marketplace**。內含文獻研究、標準寫作與 plant 建模的團隊 skills，供團隊成員一鍵安裝。

## 安裝方式

**Claude Code（CLI）**

```
/plugin marketplace add aaronchang-068/research-suite
/plugin install research-suite@research-suite
/reload-plugins
```

**桌面 App**：Settings → Plugins → Add → **Add from a repository**，輸入
`aaronchang-068/research-suite`，再安裝 `research-suite`。

## 內含 skills（1 個 plugin：`research-suite`）

兩條主線，都是把工作經驗寫成 SOP：

### 1. 研究流程與報告撰寫

| skill | 用途 |
|---|---|
| `pxa-scout` | 文獻缺口探勘（引用鏈滾雪球 snowballing＋figures 奠基者錨定） |
| `pxa-literature` | 文獻研究 SOP（source → atomic → MOC → 工程文件草稿） |
| `pxa-scribe` | 盤問研究需求 → 證據盤點（vault 優先，無 vault 依專案編排規則或詢問）→ roadmap → NASA-TP 等級報告（documents/{STRN}.md，MD 先行） |
| `pxa-standards` | SP 技術報告標準寫作規範檢查 |
| `pxa-mentor` | 研究知識庫互動式導師（讀 vault、以體系主人思維精簡答問） |
| `pxa-latexer` | scribe 定稿 Report.md → LaTeX 紙本歸檔版（.tex，XeLaTeX） |

### 2. MATLAB / Simulink 檔案建立與資料夾分類

| skill | 用途 |
|---|---|
| `pxa-matlab-project` | 專案資料夾分類與檔案歸類（九個固定資料夾、相依鏈、三個判斷問句、產出雙軌；新專案範本、盤點與搬移流程；專案 README 的 MD＋HTML 雙軌） |
| `pxa-modeler` | plant 數學模型建模工作流（三種證據 → 保真度分層 L1–L3 → 驗證階梯；工具操作配合 MathWorks 官方 skill） |
| `pxa-matlab-style` | MATLAB m-file 撰碼風格（檔頭、分段、對齊、命名、單位換算、輸出與繪圖；統一既有檔案的流程） |

安裝後呼叫方式：`/research-suite:pxa-scout`、`/research-suite:pxa-literature` … 以此類推。

## 更新

```
/plugin marketplace update research-suite
```

## Repo 結構

```
.claude-plugin/
  ├─ marketplace.json   ← marketplace 清單（列出 plugin；不宣告 skills）
  └─ plugin.json        ← plugin 身分檔
skills/                 ← plugin 安裝時自動探索此目錄下的每個 skill
  ├─ pxa-scout/         （各含 SKILL.md）
  ├─ pxa-literature/
  ├─ pxa-scribe/
  ├─ pxa-standards/
  ├─ pxa-mentor/
  ├─ pxa-latexer/
  ├─ pxa-modeler/
  ├─ pxa-matlab-style/
  └─ pxa-matlab-project/
```
