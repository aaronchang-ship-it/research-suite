# <PROJECT> — Claude 專案協作指引

> 繁中優先；技術術語 / 檔名 / 工具名 / 法規名保留英文原文。
> 本檔為 Claude 在本專案的工作規則，`<負責人>` 為唯一裁定者。
> 範本：把 `<PROJECT>` / `<project>` / `<負責人>` 取代成自己的內容，各節依專案增刪。

---

## 0. 每次對話開場
1. 一個對話只聚焦一件事。
2. 需架構決策的工作（新腳本架構、新模型分層）→ 先在對話討論定案，再動手。

## 1. 專案身份
| 項目 | 內容 |
|---|---|
| 專案 | <專案全名> |
| 平台 | MATLAB / Simulink <版本>；MATLAB Project = `<PROJECT>.prj` |
| 範疇 | <設計 / 驗證 / 參數 / 資料分析> |
| Toolbox | <列出所需 toolbox> |

## 2. 授權範圍與寫入流程（硬規則）
| 動作 | 規則 |
|---|---|
| 讀取 / 分析 | 全專案可讀 |
| 寫入（新增 / 修改 / 搬移 / 改名） | 只限 `<負責人>` 指定的檔案；先列「寫入清單」→ 明確回覆確認 → 才執行；確認只對該次清單有效。未指定的檔案即使發現問題也只回報、不動 |
| 刪除 | 不執行；列出清單，由 `<負責人>` 自行刪除 |
| git | Claude 只跑唯讀指令（一律加 `--no-optional-locks`）；不 add / commit / push / reset / checkout / restore |

### 2.1 寫入流程
1. **基線**：寫入前確認 git 工作區乾淨，確保每次寫入都能 `git diff` 檢視、`git restore` 還原。
2. **寫入清單**：列出 `# × 檔案 × 動作 × 變更摘要`；修改既有檔附 diff，等確認。
3. **最小變更**：只改清單上的行；不順手重排、重格式化、改名。
4. **回報**：寫入後回報 `git --no-optional-locks diff --stat`，由 `<負責人>` review 後自行 commit。

### 2.2 保護清單（需逐檔指名才可改）
- `*.slx`、`*.slx.autosave`、`*.asv`、`workspace\*.mat`、`model\`
- 已驗證流程的腳本：<列出檔名>
- 絕不觸碰：`.git\`、`cache\`、任何 `slprj\`、`resources\`

## 3. MATLAB 撰碼準則
依 MathWorks MATLAB Coding Guidelines；以下為專案慣例，衝突時以本節為準。

### 3.1 版面
| 項目 | 規則 |
|---|---|
| 行寬 | ≤ 75 字元（含檔頭註解）；超過用 `...` 斷行，續行縮排 4 空格 |
| 分段 | 只用 `%%`（cell section） |
| 分隔線 | 禁用 `% ====`、`% ----`、`% ***` 等 banner 分隔 |
| 註解位置 | 註解一律放在程式碼上一行；禁止行尾註解 |
| 單位標註 | 寫在上一行註解尾，格式 `% <description>, <unit>` |
| 縮排 | 4 空格，不用 tab |
| 一行一敘述 | 禁止同行多敘述（唯一例外：檔頭 `clear all; close all; clc`） |
| 空白 | 逗號後一格；`=`、關係、邏輯運算子兩側各一格；`:` `*` `/` `^` 不留空白 |
| 字串 | 新程式用 `"`；修改既有檔時沿用該檔原有引號風格 |

### 3.2 函式使用
- 優先 MATLAB / Toolbox 內建函數，不自造輪子。
- 模擬用 `Simulink.SimulationInput` + `setVariable` / `setModelParameter`，取代 `assignin` 與散落的 base workspace 變數。
- 不用匿名函數包裝重複呼叫；每行明寫呼叫。
- 禁用 / 慎用：`global`、`eval` / `evalin` / `assignin`、command syntax。
- 顯示 / 繪圖用工程單位（deg、deg/s）；內部運算維持 SI。

### 3.3 命名
| 對象 | 規則 |
|---|---|
| 檔名 / 函式 | `<project>_<domain>_<purpose>` snake_case |
| 區域變數 | lowerCamelCase；數學 / 物理符號可用短名；避免負向名 |
| 新函式 | 動詞 / 名詞片語；邏輯輸出 `is` / `has` 開頭；≤ 32 字元 |
| 類別 | UpperCamelCase |

### 3.4 結構
- 檔名 = 頂層函式名；所有函式以 `end` 收尾。
- 輸入 ≤ 6、輸出 ≤ 4；可選參數用 Name=Value；public 函式用 `arguments` 區塊。
- 迴圈前 pre-allocate；巢狀 ≤ 5 層。
- 浮點勿用 `==` / `~=`；`switch` 必含 `otherwise`。
- 清光 Code Analyzer 警告（不以 `%#ok` 壓警告）。

### 3.5 註解語言
程式碼註解一律英文；文件（`.md`）維持繁中。

## 4. 檔頭範本
腳本用下列結構，無關欄位省略；每行 ≤ 75 字元。

```matlab
%% <PROJECT> <Domain> <Title of the Script / Analysis>
%
% Strategy: <approach, wrap at 75 chars with aligned indent>
%
% Per MathWorks guidance:
%   "<verbatim quote from the doc page>"
%
%   Ref: <Doc page title> (MathWorks <Toolbox>)
%
% Workflow:
%   1. <step>
%   2. <step>
%
% Model:     <simulink model name>
% Author:    <name>
% Modified:  YYYY-MM-DD HH:MM:SS (GMT+8)
%   - <this change, English>
%
% Copyright <year> <company>
```

| 欄位 | 規則 |
|---|---|
| Per MathWorks guidance | 只在遵循官方文件方法時列；引文須當下查核原文逐字引用，查不到就整段省略 |
| Modified | 只列本次變更，不累積舊紀錄（版本歷程由 git 管理） |
| Copyright | 檔頭最末列；`<year>` = Modified 年份 |

- 函式：H1 line 緊接 `function` 宣告，再接 Syntax / Inputs / Outputs / See also。
- 檔頭後第一段程式：`clear all; close all; clc` → `%% Initialization`。

## 5. 專案慣例（勿擅改）
| 領域 | 慣例 |
|---|---|
| 模型分層 | 相依鏈：`data\` → `workspace\*.mat` → `library\` → `model\` → {`design\`, `harness\`}。判斷：換機型只換參數就能用 → `library\`；拿來 trim / 線性化 / 跑 SIL → `model\`；刪掉後整機模擬仍能跑 → `harness\`。library `.slx` 不直接讀 `data\`，數值一律由 `workspace\*.mat` 提供；harness 的比對資料直接讀 `data\`，不另存副本；取參數與驗證不用同一筆資料 |
| 設計 / 模擬產出 | 雙軌：`.mat` 一律存 `workspace\`；同時輸出人類可讀的 `.xlsx` / `.txt` / 參數檔到 `output\`。例外：工具 session 檔留在 `design\` 原處 |
| 分系統資料 | `data\<分系統>\{source, mat, figure}`；`source`＝原始交付（只增不改）、`mat`＝轉出的 `.mat`、`figure`＝分析圖；腳本放分系統根目錄 |
| 整合測試資料 | `data\<階段>\`，階段＝`sil` / `hil1` / `hil2` / `ft`；跨階段共用腳本放 `data\` 根目錄 |
| 結果檔 | 每 case 收進 struct array，一次存 `workspace\<project>_<DOMAIN>_<Stage>Results.mat` |
| 版本控制 | 以 git 管理；變更歷程看 commit，不寫在檔頭；commit 由 `<負責人>` 執行 |

## 6. 繪圖慣例
| 項目 | 規則 |
|---|---|
| figure | `Color="w"`；所有 figure 同一大小（方便做簡報），於腳本開頭定義一次 |
| axes | 字型、字級全專案一致；`grid on` |
| 版面 | 一張圖不塞太多列 subplot / tile（建議 ≤ 3 列） |
| 頻譜類 | `YScale="log"`；`XLim` 依頻帶、`YLim` 依資料量級 |
| legend | `Location="best"`；多通道比較疊在同一張圖 |
| 標籤 | 軸標含單位：`Time (s)`、`Pitch rate (deg/s)` |

## 7. 輸出風格
簡潔、表格化、重點先行；第一行給結論 / 下一步。有選擇時列「選項 × 差異 × 取捨」＋最多一行推薦，不替 `<負責人>` 做決定。假設與模型係數要明列，不憑空加保守倍數。

## 8. 資料夾速查
| 資料夾 | 用途 | 權限 |
|---|---|---|
| `CLAUDE.md`、`README.md` | 協作指引 / 專案說明 | 寫入需確認 |
| `data\` | 分系統資料（`source` / `mat` / `figure` ＋ 根目錄腳本）；整合測試階段 `sil` / `hil1` / `hil2` / `ft` | 寫入需確認 |
| `workspace\` | `.mat` 集中區；各腳本統一由此讀寫 | 寫入需確認 |
| `library\` | 通用次系統 library `.slx`；參數來自 `workspace\*.mat` | 寫入需確認 |
| `model\` | 主 plant 模型（整機組裝；不含測試） | 寫入需確認 |
| `design\` | init / trim / linearize / design / sim，依 domain 分子資料夾 | 寫入需確認 |
| `harness\` | 次系統開迴路驗證、library 模組獨立驗證 | 寫入需確認 |
| `veristand\` | SIL / HIL 即時目標機模型 | 寫入需確認 |
| `output\` | 人類可讀產出：`.xlsx` / `.txt` / 參數檔 / 圖檔 | 寫入需確認 |
| `documents\` | 技術報告草稿（`.md`） | 寫入需確認 |
| `cache\` `resources\` `.git\` | 建置快取 / Project 資源 / 版本庫 | 勿動 |

## 9. 典型工作流程
```
<project>_<domain>_init → <project>_<domain>_trim
→ <project>_<domain>_linearize → <project>_<domain>_design
→ <project>_<domain>_sim
```
