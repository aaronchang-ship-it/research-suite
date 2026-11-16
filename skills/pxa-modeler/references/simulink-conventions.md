# Simulink 建模判斷與版面慣例

> pxa-modeler 的參考檔。這裡只放「怎麼把數學模型落成方塊」的判斷與版面習慣；
> 工具怎麼操作照 MathWorks 官方 skill（`building-simulink-models`、
> `arranging-simulink-layouts`）。

## 1. 建模判斷
| 項目 | 規則 | 理由 |
|---|---|---|
| 方塊 | equation-based，主路徑全用基本方塊；狀態機 / 迴圈才用 MATLAB Function | 式子與方塊一對一，可 codegen |
| 型別 / 取樣 | `double`；固定步長，步長依專案 | 與飛控、HIL 對齊 |
| 快子狀態 | 時間常數遠小於步長的子狀態用 ZOH 精確離散解，不靠縮小步長 | 步長由整機決定，不由單一模組決定 |
| algebraic loop | 方塊內不得有，用封閉解；整合層必要時以一步 Memory 切斷並註明 | 固定步長、可 codegen |
| 介面 | 模組是 atomic subsystem；埠名含物理意義；埠保留上游給的**物理量**（例：軸向速度），換算成查表變數（例：進距比）在方塊內做 | 上游資料一定以物理量到達 |
| 輸出 | 盡量對齊飛控 log 的欄位 | 回放時直接比對 |
| 參數 | 方塊參數引用參數 struct 欄位；Gain 以參數意義命名 | 換型號只換 struct |
| 可線性化 | 增益 / 濾波在主路徑，飽和 / 切換在旁；檢查 Saturation 的 `LinearizeAsGain` 與 Transport Delay 的 Padé 階數 | L1 要能交給控制設計 |
| 查表 | 每個索引訊號進表前先過 Saturation，限制在第一與最後一個斷點；`Binary search`、外插 Clip | 保證查表在有效範圍內 |
| 保護 | 旗標只舉旗不切斷；除法加下限保護，且只用在除法 | 切斷屬保護電路或飛控 failsafe |

## 2. 版面慣例
- 左進右出；主訊號流排成一列（命令 → 迴路 → 限制 → 積分 → 輸出）。
- 回授方塊翻面放在主列下方；限制與旁支計算放在主列上方，從上方進入限制方塊；
  電流、功率等衍生輸出放右上。
- Sum 用圓形；可變上下限用一個 Saturation Dynamic，不用 MinMax 成對。
- 沒用到的 Inport 與 Terminator 集中在左上。
- 區塊用彩色 Area 標名；主路徑訊號命名。

目的：一眼看出迴路的主訊號流。

## 3. 沿用手排版面
使用者手排過的方塊是範本。同結構的方塊（例如另一個等級）複製它再改差異：
- 用 `model_edit` 的 `configure Position` 逐塊放置，`layout_mode` 用 `incremental`。
- 不對手排過的圖做 full layout，也不用 `Simulink.BlockDiagram.arrangeSystem`。
- 動手前先存一份副本；agent 的編輯不能靠 Ctrl+Z 還原。
