# <PROJECT> — <專案全名>

> 本資料夾為 MATLAB / Simulink 專案的分類範本。
> 使用時把 `<PROJECT>`（顯示名）與 `<project>`（檔名前綴，小寫）取代成自己的專案代號。

<一段話說明專案：機型 / 產品、範疇（設計、驗證、參數、資料分析）。>

完整說明書（架構圖、資料交換、流程、現況盤點）見 `README.html`。

---

## 快速開始
1. 以 MATLAB 開啟 `<PROJECT>.prj`（自動設定路徑）。
2. 進入 `design\<domain>\`。
3. 先跑 `*_init` 載入參數，再依「典型工作流程」往下。

## 資料夾結構
| 資料夾 | 用途 | 放什麼 |
|---|---|---|
| `data\` | 依整合層級編排的資料 | 模組與分系統的原始交付、轉出的 `.mat`、分析圖、該層專屬的腳本與模型；SIL / HIL / 飛測的 ulog |
| `workspace\` | `.mat` 集中區 | 參數、trim / 線性化 / 設計結果；各腳本統一由此讀寫 |
| `library\` | 通用次系統 library `.slx`；跨階段共用的 `.m` 工具 | 推進、風場、大氣等獨立建模的模組；`library\ulog\`（ulog 讀取與繪圖工具） |
| `model\` | 主 plant 模型 | 整機組裝模型；不含測試 |
| `design\` | 設計腳本 | init / trim / linearize / design / sim，依 domain 分子資料夾 |
| `harness\` | 驗證 | 次系統開迴路驗證、library 模組獨立驗證（`.slx` ＋ 測試 `.m`） |
| `veristand\` | SIL / HIL 即時目標機模型 | 即時目標機用的包裝模型與 init / sim 腳本 |
| `output\` | 人類可讀產出 | `.xlsx` / `.txt` / 參數檔 / 圖檔；交接其他分系統或作報告素材 |
| `documents\` | 技術報告草稿 | `.md` |
| `temp\` | 收件匣 | 新收到、尚未分類的檔案；歸檔後清空 |
| `README.md`、`README.html`、`CLAUDE.md` | 專案說明（文字精簡版 / 完整說明書）/ Claude 協作指引 | 放專案根目錄 |

`cache\`、`*\slprj\`、`resources\` 由 MATLAB / Simulink 自動產生，勿手動編輯。

`temp\` 不在相依鏈內：腳本與模型不得讀取或引用 `temp\` 的路徑，也不加入 MATLAB path；常態為空。

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
第 2 層（L2）是整合層級，由下而上：module → system → simulation → ground → flight。

| L2 | 對象 | 放什麼 | L3 命名 |
|---|---|---|---|
| `module` | 單一模組（元件） | 模組本身的資料：規格、性能圖、單體測試 | 廠牌或元件名 |
| `system` | 多個模組整合成的分系統 | 多模組整合測試，或該分系統的數學模型資料 | `aerodynamics` / `propulsion` / `structure` / `performance` |
| `simulation` | 多個分系統整合，純軟體 | SIL 的 ulog | `sil` |
| `ground` | 多個分系統整合，實體硬體在地面 | HIL 的 ulog | `hil1`、`hil2` |
| `flight` | 整機 | 飛測（ft）的 ulog 與飛後分析 | 無，檔案直接放 `flight\` |

判斷：只涉及一個元件 → `module`；多個元件組成一個分系統，或是該分系統的數學模型 → `system`；
多個分系統整合：純軟體 → `simulation`，有實體硬體且在地面 → `ground`，實際飛行 → `flight`。
整機性能是數學模型資料，歸 `system\performance`。

### `module`、`system` 的 L3 內部
```
data\module\<元件>\   或   data\system\<分系統>\
├─ source\   原始交付（csv / txt / xlsx），只增不改
├─ mat\      由 source 轉出的 .mat
├─ figure\   分析圖
└─ *.m、*.slx   該 L3 專屬的分析腳本、設計腳本與模型檔（不另開 scripts、model）
```
- `source` / `mat` / `figure` 底下可再依測試分子資料夾（例 `structure\source\gvt\`）。
- 只測單一分系統特性的試驗（例：GVT）屬該分系統，放 `system\structure`。

### `simulation`、`ground`、`flight`
只收四個階段的 ulog，資料夾內平放，靠檔名排序：

| 階段 | 位置 | 定義 |
|---|---|---|
| SIL | `data\simulation\sil\` | 純軟體迴路模擬 |
| HIL1 | `data\ground\hil1\` | 部分硬體（例：電池＋推進）＋模擬器，檢驗硬體迴路下的功能性與穩定性 |
| HIL2 | `data\ground\hil2\` | 結構＋激振器＋模擬器，檢驗結構耦合下的功能性與穩定性 |
| FT | `data\flight\` | 實機飛行測試 |

- 機上地面測試（非 HIL）資料不在收件範圍。
- 四個階段共用的 ulog 讀取與繪圖工具放 `library\ulog\`，不放 `data\` 根目錄。

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
- ulog：`<階段>_<機型版本>_NO<架次>_<YYYYMMDD>_<HHMM>`（例 `HIL1_<機型>MK20_NO001_20261122_1430.ulg`）；
  階段大寫（`SIL` / `HIL1` / `HIL2` / `FT`）、版本兩碼不含小數點、架次三碼補零、時間 24 小時制；
  衍生檔（`.mat`、`.csv`、圖）沿用同一主檔名。
- m-file 檔頭 `Modified: YYYY-MM-DD HH:MM:SS (GMT+8)`，只列本次變更；歷程以 git 管理。
- MATLAB 撰碼風格與檔頭範本：見 `CLAUDE.md`。

## 開發環境
- 版本控制：git。
- MATLAB + Simulink <版本>。
- Toolbox：<列出所需 toolbox>。

## 作者
<姓名> — <公司 / 單位>
