# matlab-style skill — CHANGELOG

## v0.2（2026-11-21，plugin 1.15.0）

起因：v0.1 是個人 skill，只在一台機器上；本版依九支現行 `.m`（控制設計腳本與兩支共用函式、
電池回放與 preset 腳本、馬達與螺旋槳 preset 腳本、獨立模擬腳本）歸納後移入 research-suite。
專案名稱、型號、單位名稱等專屬內容未帶入，範例改為通用寫法。

| # | 變更 | 落點 |
|---|------|------|
| 1 | 檔頭範本寫進 skill（原本指向專案 `CLAUDE.md`）：腳本、函式檔、local function 三種 | §2 |
| 2 | 「Per MathWorks guidance」只在本次對話讀過文件頁時才引用 | §2.1 |
| 3 | 分段：`%% Initialization` → `%% Step N:`（對應 Workflow）→ `%% Local Functions` | §3 |
| 4 | 數值表與文字表的寫法；參數 struct（型號命名、扁平一層、`<?>` 標記、來源資料原樣保留） | §5.2、§5.3 |
| 5 | 具名常數的寫法（換算方向、單位、來源）；調整值一律具名 | §9 |
| 6 | 輸出：欄名帶單位字尾、`RowNames`、進度與存檔訊息、共用表格函式 | §10 |
| 7 | 繪圖：`DefaultLineLineWidth`、`tiledlayout` 間距、線型與顏色慣例、`exportgraphics` | §11 |
| 8 | 路徑兩種寫法；`Simulink.SimulationInput`；只關自己載入的模型；`save` 明列變數 | §12 |
| 9 | 匿名函數例外：求解器的目標函數 handle | §12 |
| 10 | 命名補充：`was` 開頭、`flag.<name>`、`<what>File` / `<what>Dir`、`fig<What>` / `ax<What>`、錯誤訊息 | §13 |
| 11 | 統一流程補充：被呼叫腳本以變數名讀 workspace 時不可改名；`subplot`、逐軸 `set(gca)` 列入風格修正 | §14 |

沿用 v0.1、未放寬的規則（現行檔案中仍有不符之處，統一時依 §14 處理）：
iterator 不用 `k`、等號成組對齊、不用 `subplot` 與逐軸 `set(gca, ...)`、本文不再出現清除指令、
角度換算用 `convang`、換算係數具名。

待辦：
- 待決事項 a（字體階層、標題與圖號）、b（case table 列說明位置）、c（黃金範例檔）。

## v0.1（2026-10-30）

個人 skill 草稿，經四輪問答建立：版面、等號對齊、case table、迴圈、switch、字串與 Name-Value、
Toolbox 單位換算、`disp(table)`、繪圖預設、命名、統一既有檔案的流程。
