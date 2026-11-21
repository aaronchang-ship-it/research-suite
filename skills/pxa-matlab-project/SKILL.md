---
name: pxa-matlab-project
description: MATLAB / Simulink 專案的資料夾分類與檔案歸類 SOP：九個固定的第 1 層資料夾（data / workspace / library / model / design / harness / veristand / output / documents）、相依鏈、三個判斷問句、分系統資料與整合測試資料的編排、機器讀與人讀的產出雙軌、命名規則，以及搬移檔案時的清單、確認與 MATLAB Project 路徑同步。凡使用者提到建立新的 MATLAB 專案、專案範本、資料夾結構、資料夾分類、檔案該放哪裡、整理或盤點專案資料夾、搬移或改名 .m / .slx / .mat、新增一個 domain 或分系統的資料夾——即使沒有明說 skill 名稱——都應使用本 skill。建模工作流屬 pxa-modeler、.m 撰碼風格屬 pxa-matlab-style；本 skill 只管「檔案放哪裡、叫什麼、怎麼搬」。
argument-hint: "[選填：新專案代號，或要歸類 / 盤點的檔案與資料夾]"
---

# matlab-project — MATLAB / Simulink 專案資料夾分類與檔案歸類 v1.0

> 📋 版本變更見 `CHANGELOG.md`。
> 範本：`templates/CLAUDE.md`、`templates/README.md`（新專案直接複製後取代佔位字）。

定位：research-suite 的 MATLAB / Simulink 這條線共三個 skill——本 skill 管檔案放哪裡，
`pxa-modeler` 管模型怎麼建與驗證，`pxa-matlab-style` 管 `.m` 怎麼寫。

**優先順序**：專案自己的 `CLAUDE.md` > 本 skill。專案已經有自己的資料夾規則時，照專案的；
本 skill 只在專案沒有規則、或使用者要求照範本整理時才作為依據。不主動提議把既有專案改成範本結構。

## 1. 三種工作

| 工作 | 觸發 | 產出 |
|---|---|---|
| A. 建立新專案 | 「開一個新專案」「照範本建資料夾」 | 資料夾骨架、`CLAUDE.md`、`README.md`（§7） |
| B. 歸類檔案 | 「這個檔案放哪裡」、寫新檔之前 | 一行結論：位置＋檔名＋依據（§3、§4） |
| C. 盤點既有專案 | 「整理資料夾」「檢查有沒有放錯」 | 盤點表 → 搬移清單 → 確認後執行（§8） |

寫任何新檔之前都先做 B：先決定位置與檔名，再寫內容。

## 2. 第 1 層資料夾（用詞固定，不自行新增）

| 資料夾 | 用途 | 放什麼 |
|---|---|---|
| `data\` | 各分系統交付的資料、整合測試資料 | 原始交付、轉出的 `.mat`、分析圖、前處理腳本 |
| `workspace\` | `.mat` 集中區 | 參數、trim / 線性化 / 設計結果；各腳本統一由此讀寫 |
| `library\` | 通用次系統 library `.slx` | 推進、風場、大氣等獨立建模的模組 |
| `model\` | 主 plant 模型 | 整機組裝模型；不含測試 |
| `design\` | 設計腳本 | init / trim / linearize / design / sim，依 domain 分子資料夾 |
| `harness\` | 驗證 | 次系統開迴路驗證、library 模組獨立驗證（`.slx` ＋ 測試 `.m`） |
| `veristand\` | SIL / HIL 即時目標機模型 | 即時目標機用的包裝模型與 init / sim 腳本 |
| `output\` | 人類可讀產出 | `.xlsx` / `.txt` / 參數檔 / 圖檔；交接其他分系統或作報告素材 |
| `documents\` | 技術報告草稿 | `.md` |
| 根目錄 | 專案說明與協作指引 | `README.md`、`CLAUDE.md`、`<PROJECT>.prj` |

`cache\`、`*\slprj\`、`resources\`、`.git\` 由工具自動產生，不讀寫、不搬移。

用不到的資料夾可以不開（例如沒有即時目標機就沒有 `veristand\`），但不改名、不合併。

### 2.1 相依鏈

只能由左往右相依，不可反向：

```
data\ → workspace\*.mat → library\ → model\ → { design\, harness\ }
```

| 規則 | 理由 |
|---|---|
| library `.slx` 不直接讀 `data\`；數值一律由 `workspace\*.mat` 提供 | 換機型只換參數檔，library 不用改 |
| harness 的比對資料直接讀 `data\`，不另存副本 | 驗證用的事實只有一份 |
| 取參數與驗證不用同一筆資料 | 否則驗證只是把辨識結果再讀一次 |

## 3. 模型放哪裡：三個問句

依序問，第一個答「是」的就是位置。

| # | 問句 | 是 → 放 |
|---|---|---|
| 1 | 換機型只換參數就能用？ | `library\` |
| 2 | 拿來 trim / 線性化 / 跑 SIL？ | `model\` |
| 3 | 刪掉後整機模擬仍能跑？ | `harness\` |

三題都答不出來時，不要猜：把檔案、它被誰引用、它引用誰列出來，請負責人裁定。

## 4. 檔案歸類表

| 檔案 | 位置 |
|---|---|
| 分系統交付的原始檔（csv / txt / xlsx） | `data\<分系統>\source\`，只增不改 |
| 由原始檔轉出的 `.mat` | `data\<分系統>\mat\` |
| 資料分析後的圖 | `data\<分系統>\figure\` |
| 前處理 / 分析原始資料的 `.m` | `data\<分系統>\` 根目錄（不另開 scripts） |
| 整合測試的 log 與紀錄 | `data\<階段>\`（§5.2） |
| 跨階段共用的分析 `.m` | `data\` 根目錄 |
| 模型執行時要讀的參數 `.mat` | `workspace\` |
| trim / 線性化 / 設計 / 模擬結果 `.mat` | `workspace\<project>_<DOMAIN>_<Stage>Results.mat` |
| library `.slx` | `library\` |
| 整機組裝模型 `.slx` | `model\` |
| init / trim / linearize / design / sim 的 `.m` 與其線性模型 | `design\<domain>\` |
| 設計工具的 session 檔與自動產生的 tuner 腳本 | `design\<domain>\` 原處（例外，不搬到 `workspace\`） |
| 驗證用 `.slx` 與測試 `.m` | `harness\` |
| 即時目標機的包裝模型與 init / sim 腳本 | `veristand\` |
| 交接用的 `.xlsx` / `.txt` / 參數檔、報告用圖檔 | `output\`（依 domain 或用途分子資料夾） |
| 技術報告草稿 | `documents\` |

規則沒有列到的檔案種類（例如論文 PDF、規格書、第三方程式、要停用的舊檔）：
不自創資料夾名稱，列出檔案與兩個候選位置，請負責人裁定，並把裁定寫進專案 `CLAUDE.md`。

## 5. `data\` 的編排

### 5.1 分系統資料

```
data\<分系統>\
├─ source\   分系統原始交付（csv / txt / xlsx），只增不改
├─ mat\      由 source 轉出的 .mat
├─ figure\   分析後圖檔
└─ *.m       前處理 / 分析腳本
```

- 分系統例：`aerodynamics`、`performance`、`propulsion`、`structure`。
- `source` / `mat` / `figure` 底下可以再依測試分一層（例 `structure\source\gvt\`）。**最深到這一層為止**。
- 只測單一分系統特性的試驗（例：地面振動試驗）屬分系統資料，不放整合測試。

### 5.2 整合測試資料

`data\<階段>\`，依測試階段分：

| 階段 | 定義 |
|---|---|
| `sil` | 純軟體迴路模擬 |
| `hil1` | 部分硬體（例：電池＋推進）＋模擬器，檢驗硬體迴路下的功能性與穩定性 |
| `hil2` | 結構＋激振器＋模擬器，檢驗結構耦合下的功能性與穩定性 |
| `ft` | 實機測試 |

## 6. 產出與命名

### 6.1 產出雙軌

| 軌 | 位置 | 格式 | 給誰 |
|---|---|---|---|
| 機器讀 | `workspace\` | `.mat` | 下游腳本 |
| 人讀 | `output\` | `.xlsx` / `.txt` / 參數檔 / 圖檔 | 其他分系統、報告 |

設計與模擬腳本兩軌同時輸出：每個 case 收進 struct array，一次存一個結果檔；
同一份結果再寫成人看得懂的表與圖。腳本每次執行覆寫 `output\` 的同名檔，歷程交給版本控制。

### 6.2 命名

| 對象 | 規則 |
|---|---|
| `.m` / `.slx` 檔名 | `<project>_<domain>_<purpose>`，snake_case；離開資料夾仍看得出歸屬 |
| 結果檔 | `workspace\<project>_<DOMAIN>_<Trim/Linearized/Design>Results.mat` |
| 資料檔日期 | `YYMMDD` 或 `YYYYMMDD` |
| 典型流程 | `_init` → `_trim` → `_linearize` → `_design` → `_sim`，每一步的輸入是上一步的結果檔 |

`.m` 的檔頭、分段與撰碼風格見 `pxa-matlab-style`。

## 7. 工作 A：建立新專案

1. 問清楚三件事：專案顯示名 `<PROJECT>`、檔名前綴 `<project>`（小寫）、有哪些 domain 與分系統。
2. 列寫入清單（要建的資料夾、兩份範本檔）→ 負責人確認。
3. 建第 1 層資料夾（用不到的不建）；空資料夾要進版本控制時放 `.gitkeep`。
4. 複製 `templates/CLAUDE.md`、`templates/README.md` 到專案根目錄，把 `<PROJECT>`、`<project>`、
   `<負責人>`、版本與 toolbox 取代成實際內容；範本中不適用的節刪掉，不留空欄。
5. MATLAB Project（`.prj`）由負責人在 MATLAB 建立，或依 MathWorks 官方 skill
   `managing-simulink-projects` 操作；`library\`、`model\`、`design\<domain>\`、`harness\` 上 project path，
   `data\`、`workspace\`、`output\`、`documents\` 不上 path（腳本以相對專案根目錄的路徑讀寫）。
6. 回報建立了什麼、哪些佔位字還沒填。

## 8. 工作 C：盤點與搬移

搬移是高風險動作：腳本裡寫死的路徑、project path、版本控制都會受影響。**先盤點、後列清單、確認才動。**

### 8.1 盤點（唯讀）

1. 列出第 1 層與第 2 層；標出不在 §2 用詞內的資料夾、深度超過 §5 的資料夾。
2. 逐檔依 §3、§4 判定應在位置；判不出來的另列。
3. 每個要搬的檔案，搜尋誰引用它：檔名字串、`load` / `save` / `readtable` 的路徑、
   `load_system` / `sim` 的模型名、library link、model reference。
4. 輸出盤點表：

| # | 檔案 | 現在位置 | 建議位置 | 依據 | 受影響的檔案 |
|---|---|---|---|---|---|

### 8.2 搬移（寫入）

| 步驟 | 規則 |
|---|---|
| 清單 | `# × 檔案 × 動作 × 變更摘要`，連同要跟著改路徑的腳本行號一起列；負責人確認後才執行，確認只對該次清單有效 |
| 基線 | 動手前確認版本控制工作區乾淨，搬完才能逐檔比對與還原 |
| 保護檔 | `.slx`、`.mat`、原始資料要逐檔指名才搬；原始資料搬移後內容必須位元組相同 |
| 不刪除 | 要停用的檔案列出來交給負責人處理，不自行刪除 |
| 路徑 | 搬完同步改腳本裡的相對路徑；只改清單上的行 |
| project path | 搬動或改名後同步 MATLAB Project 的檔案清單與 path（官方 skill `managing-simulink-projects`） |
| 驗證 | 重新開啟 Project；受影響的腳本與模型至少各跑一次或做 update diagram；回報版本控制的差異統計 |

已知的坑：

- 開啟 MATLAB Project 時，仍在 project path 上但已不存在的資料夾會被自動重建——先改 path 再搬。
- 把檔案加進 Project 會自動把它加入版本控制的暫存區；版本控制由負責人操作的專案要事先說明。
- library link 與 model reference 以**名稱**解析，只要新位置在 path 上就不會斷；寫死相對路徑的
  `load` / `save` 才會斷。
- `slprj\` 與 `*.slxc` 是快取，不搬；搬完模型後由 MATLAB 重新產生。

## 9. 回報格式

- 工作 B：一行結論——`放 <位置>\<檔名>，依據 <§3 問句或 §4 列>`。
- 工作 A、C：第一行結論，其後表格；最後列出尚待負責人裁定的項目。
- 規則沒涵蓋、或專案規則與本 skill 不同之處，只回報、不自行決定。
