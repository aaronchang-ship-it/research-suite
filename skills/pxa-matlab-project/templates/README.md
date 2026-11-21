# <PROJECT> — <專案全名>

> 本資料夾為 MATLAB / Simulink 專案的分類範本。
> 使用時把 `<PROJECT>`（顯示名）與 `<project>`（檔名前綴，小寫）取代成自己的專案代號。

<一段話說明專案：機型 / 產品、範疇（設計、驗證、參數、資料分析）。>

---

## 快速開始
1. 以 MATLAB 開啟 `<PROJECT>.prj`（自動設定路徑）。
2. 進入 `design\<domain>\`。
3. 先跑 `*_init` 載入參數，再依「典型工作流程」往下。

## 資料夾結構
| 資料夾 | 用途 | 放什麼 |
|---|---|---|
| `data\` | 各分系統產出資料、整合測試資料 | 原始交付、轉出的 `.mat`、分析圖、前處理腳本 |
| `workspace\` | `.mat` 集中區 | 參數、trim / 線性化 / 設計結果；各腳本統一由此讀寫 |
| `library\` | 通用次系統 library `.slx` | 推進、風場、大氣等獨立建模的模組 |
| `model\` | 主 plant 模型 | 整機組裝模型；不含測試 |
| `design\` | 設計腳本 | init / trim / linearize / design / sim，依 domain 分子資料夾 |
| `harness\` | 驗證 | 次系統開迴路驗證、library 模組獨立驗證（`.slx` ＋ 測試 `.m`） |
| `veristand\` | SIL / HIL 即時目標機模型 | 即時目標機用的包裝模型與 init / sim 腳本 |
| `output\` | 人類可讀產出 | `.xlsx` / `.txt` / 參數檔 / 圖檔；交接其他分系統或作報告素材 |
| `documents\` | 技術報告草稿 | `.md` |
| `README.md`、`CLAUDE.md` | 專案說明 / Claude 協作指引 | 放專案根目錄 |

`cache\`、`*\slprj\`、`resources\` 由 MATLAB / Simulink 自動產生，勿手動編輯。

## 模型分層
相依鏈（只能由左往右相依，不可反向）：

```
data\ → workspace\*.mat → library\ → model\ → { design\, harness\ }
```

一個模型 / 模組該放哪裡，用三個問題判斷：

| 問題 | 是 → 放 |
|---|---|
| 換機型只換參數就能用？ | `library\` |
| 拿來 trim / 線性化 / 跑 SIL？ | `model\` |
| 刪掉後整機模擬仍能跑？ | `harness\` |

規則：
- library `.slx` 不直接讀 `data\`；數值一律由 `workspace\*.mat` 提供。
- harness 的比對資料直接讀 `data\`，不另存副本。
- 取參數與驗證不用同一筆資料。

## 資料編排（`data\`）
### 分系統資料
```
data\<分系統>\
├─ source\   分系統原始交付（csv / txt / xlsx），只增不改
├─ mat\      由 source 轉出的 .mat
├─ figure\   分析後圖檔
└─ *.m       前處理 / 分析腳本（放分系統根目錄，不另開 scripts）
```
- 分系統例：`aerodynamics` / `performance` / `propulsion` / `structure`。
- `source` / `mat` / `figure` 底下可再依測試分子資料夾（例 `structure\source\gvt\`）。

### 整合測試資料
`data\<階段>\`，依測試階段分：

| 階段 | 定義 |
|---|---|
| `sil` | 純軟體迴路模擬 |
| `hil1` | 部分硬體（例：電池＋推進）＋模擬器，檢驗硬體迴路下的功能性與穩定性 |
| `hil2` | 結構＋激振器＋模擬器，檢驗結構耦合下的功能性與穩定性 |
| `ft` | 實機測試（飛行測試） |

- 只測單一分系統特性的試驗（例：GVT）屬分系統資料，放 `data\<分系統>\`。
- 跨階段共用的分析腳本放 `data\` 根目錄。

## 產出雙軌
| 軌 | 位置 | 格式 | 給誰 |
|---|---|---|---|
| 機器讀 | `workspace\` | `.mat` | 下游腳本 |
| 人讀 | `output\` | `.xlsx` / `.txt` / 參數檔 / 圖檔 | 其他分系統、報告 |

設計 / 模擬腳本兩軌同時輸出。例外：工具 session 檔（例 Control System Tuner）僅供區域設計使用，留在 `design\` 原處。

## 典型工作流程
```
<project>_<domain>_init → <project>_<domain>_trim
→ <project>_<domain>_linearize → <project>_<domain>_design
→ <project>_<domain>_sim
```

## 命名規範
- 檔名 / 函式：`<project>_<domain>_<purpose>`，snake_case。
- 結果檔：`workspace\<project>_<DOMAIN>_<Trim/Linearized/Design>Results.mat`。
- 資料檔以 `YYMMDD` 或 `YYYYMMDD` 標日期。
- m-file 檔頭 `Modified: YYYY-MM-DD HH:MM:SS (GMT+8)`，只列本次變更；歷程以 git 管理。
- MATLAB 撰碼風格與檔頭範本：見 `CLAUDE.md`。

## 開發環境
- 版本控制：git。
- MATLAB + Simulink <版本>。
- Toolbox：<列出所需 toolbox>。

## 作者
<姓名> — <公司 / 單位>
