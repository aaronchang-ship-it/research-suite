# modeler skill — CHANGELOG

## v1.0（2026-11-16，plugin 1.11.0）

由一個 VTOL plant 建模專案的專案內 skill 通用化而來（三個模組與一個次系統的實作
經驗）。專案專屬內容（機型、型號、實測數字、資料夾路徑、log 細節、寫入授權規則）
留在原專案，未帶入。

定位：本 skill 提供**分層架構、驗證流程、決策留痕**三樣工作流；MATLAB / Simulink
的工具操作交給 MathWorks 官方 skill。

| 內容 | 落點 |
|---|---|
| 七階段工作流，每階段有關卡與對應的官方 skill | SKILL.md §1 |
| 三種證據；保真度由證據決定；黑箱模組原則 | SKILL.md §2 |
| 分層架構 L1–L3、三條約束、u / w / y / z 介面分類 | SKILL.md §3 |
| 數學模型先行：方塊之前規格 md 要寫完的項目 | SKILL.md §4 |
| 驗證階梯 V1–V5、驗證性質四分類、回報紀律 | SKILL.md §5 |
| 決策與留痕 | SKILL.md §6 |
| 與官方 skill 的分工與三項明確覆寫 | SKILL.md §8 |
| Simulink 建模判斷與版面慣例 | references/simulink-conventions.md |
| 工具操作踩過的坑 | references/matlab-mcp-pitfalls.md |

與原專案 skill 的差異：
- 驗證性質由三類改四類，把「對規格書」從「自洽」分出來（規格書曲線若就是參數
  來源仍只算自洽）。
- 介面分類 u / w / y / z、「保真度由證據決定」、`StopTime` 有限值、測試與回放用
  `Simulink.SimulationInput` 取自官方 skill。
- 版面以 `model_edit` 的 `configure Position` 放置，不用 `set_param`。

待辦：
- 驗證性質四分類回寫 pxa-standards 正本，本 skill 與 pxa-scribe 改為引用。
- 保真度 L1–L3 與 `evidence_level` L1–L4、文獻層級 L1–L3 的撞名，待裁定是否改代號。
- `evals/`、`pipeline-flowchart.html` 未做。
