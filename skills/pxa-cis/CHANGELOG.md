# cis skill — CHANGELOG

## v0.1（2026-11-23，plugin 1.18.0）

建立。起因：簡報的配色與字型原本寫在 `pxa-presentation`，圖也要用到顏色；
為避免兩份，集中成一個 skill。

| 內容 | 落點 |
|---|---|
| 值分兩處（公開的中性預設值、私有品牌包）與取值順序 | SKILL.md §1 |
| 品牌包的內容與 `brand.json` 欄位 | SKILL.md §2、§3 |
| 品牌色與版面色七個角色 | SKILL.md §4 |
| 圖用的角色色與分層橫帶色 | SKILL.md §5 |
| 字型、標誌規則 | SKILL.md §6、§7 |
| 中性預設值 | `defaults/brand.json` |

由維護者裁定：
- 配色不放 `pxa-standards`，另立 `pxa-cis`。
- 三個 skill 的分工：`pxa-cis` 管顏色、字型、標誌的值；`pxa-diagram` 管圖的畫法；
  `pxa-presentation` 管簡報種類、版面與流程。
- 含標誌與單位名稱的內容放私有品牌包，公開 repo 只放中性預設值（承 `pxa-presentation` 的裁定）。

撰寫時的解讀（維護者未否決）：
- 圖用的角色色代表角色、不代表品牌，放在公開的預設值。
- 品牌包的 `brand.json` 只寫要覆蓋的欄位，其餘沿用預設值。
- 標誌的留白與可用底色因識別規範而異，數值寫在品牌包，不寫在公開的 SKILL.md。

待辦：
- 角色色的底色由圖片取色，框線色是目視估計；待取得原始檔後核對。
- `pxa-presentation` 的 `scripts/build_template.ps1` 內的色碼與字型仍是寫死的，尚未改為讀 `brand.json`。
- `pxa-scribe` 的 docx 範本、`pxa-matlab-project` 的 `README.html` 範本尚未改為引用本 skill。
- 品牌包內的標誌是點陣圖，待換成向量檔。
