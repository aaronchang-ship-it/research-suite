# diagram skill — CHANGELOG

## v0.1（2026-11-23，plugin 1.18.0）

建立骨架。起因：維護者認可一組既有的圖（方塊圖、流程圖、泳道圖共七張），要把畫法固定下來，
讓報告、簡報、專案說明書裡的圖一致。

| 內容 | 落點 |
|---|---|
| 範圍：方塊圖、流程圖、泳道圖 | SKILL.md §1 |
| 動筆前先定的四件事 | SKILL.md §2 |
| 方塊、顏色（依角色）、連線的規則 | SKILL.md §3–§5 |
| 圖例、分層橫帶、群組外框、小標籤 | SKILL.md §6 |
| 待定事項 a–g | SKILL.md §8 |

由維護者裁定：
- 畫圖獨立成一個 skill，專門做方塊圖一類的圖；使用正確的工具與語法是本 skill 的重點。
- 顏色的值放 `pxa-cis`，本 skill 只規定怎麼用。

撰寫時的解讀（維護者未否決）：
- 規則由七張圖歸納，不是由原始檔讀出；與原始檔不一致時以原始檔為準。
- 本版只收三種圖種，其他圖種之後再議。
- 圖內配色不受簡報「唯一強調色」的限制。

同一版後續加入（工具）：

| 內容 | 落點 |
|---|---|
| 工具與語法：直接寫 SVG；畫布與座標、class 對照、元素寫法 | SKILL.md §8 |
| 匯出：SVG 為原始檔，`.docx` / `.pptx` 用 2 倍 PNG | SKILL.md §9 |
| 交付前的七項檢查 | SKILL.md §10 |
| 原 §8「待定事項」順延為 §11；a、b、c、f 改為已定 | SKILL.md §11 |
| 空白範本（七個角色 class、箭頭、判斷、小標籤、圖例） | `templates/diagram_template.svg` |
| 方塊圖範例（虛構內容） | `examples/block_folder_flow.svg` |
| SVG 轉 PNG 腳本（Edge 無頭模式） | `scripts/svg2png.ps1` |

由維護者裁定：工具用「直接寫 SVG」（選項中另有 Mermaid、draw.io、描述檔＋產生器）。

撰寫時的解讀（維護者未否決）：
- 放進 `.pptx` 用 PNG，不轉成 PowerPoint 原生圖形。
- 座標格、字級、間距等數值取自試作，並以維護者認可的圖目視比對；未與原始檔核對。

同一版後續加入（依圖種選工具）：

起因：維護者另認可一份導讀 HTML 裡的圖（結構圖用 Mermaid＋ELK、示意圖用程式產生的 SVG），要求品質對齊。

| 內容 | 落點 |
|---|---|
| 範圍加入控制架構方塊圖、時序圖、狀態圖、資料驅動示意圖 | SKILL.md §1 |
| 內容寫法：線上標實際名稱、方塊寫位置與頻率、三種狀態樣式、圖說附種類、圖下說明 | SKILL.md §7 |
| 依圖種選工具的對照表；原 SVG 規則改稱 SVG 軌 | SKILL.md §8 |
| Mermaid 軌：版本、檔頭、排版設定、角色色、宣告順序 | SKILL.md §8.4 |
| 腳本產生 SVG | SKILL.md §8.5 |
| 匯出加入 `.mmd` → `.svg` | SKILL.md §9 |
| 檢查加入 Mermaid 兩項 | SKILL.md §10 |
| Mermaid 範本 | `templates/diagram_template.mmd` |
| 時序圖、流程圖範例（虛構內容） | `examples/sequence_cycle.mmd`、`examples/flow_retry.mmd` |
| Mermaid 轉 SVG 腳本 | `scripts/mmd2svg.ps1` |

由維護者裁定：
- 依圖種選工具：時序圖、流程圖用 Mermaid；控制架構方塊圖、軟體架構圖用 SVG。
- 配色一律依 `pxa-cis`；該導讀 HTML 的配色只是範例，不採用。

撰寫時的解讀（維護者未否決）：
- 狀態圖歸 Mermaid；泳道圖歸手寫 SVG（Mermaid 沒有泳道）；由數字決定位置的示意圖歸「腳本產生 SVG」。
- Mermaid 的版本固定為 11.4.1 / layout-elk 0.1.7（與該導讀相同）。
- 實測發現 Mermaid 11.4.1 不採用 `.mmd` 檔頭裡的 `layout`、`elk`、`flowchart.curve` 設定，所以排版設定改寫在 `mmd2svg.ps1` 的 `initialize`，檔頭只留主題與配色；字型要寫在 `config.fontFamily`（只寫在 `themeVariables` 不生效）。
- 節點要依流程順序宣告，否則 ELK 會把圖左右顛倒（實測）。

待辦：
- 原始檔在專案中的位置與檔名（SKILL.md §11-d），要配合 `pxa-matlab-project`。
- 泳道圖、控制架構方塊圖、狀態圖、腳本產生示意圖的範例。
- `svg2png.ps1`、`mmd2svg.ps1` 只在一台電腦上測過（Windows 11、已安裝 Noto Sans TC）；沒有該字型時的輸出未看過。
- `mmd2svg.ps1` 需要連到 jsdelivr CDN；離線時無法轉檔。
