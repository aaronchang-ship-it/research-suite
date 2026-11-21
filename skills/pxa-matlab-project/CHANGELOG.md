# matlab-project skill — CHANGELOG

## v1.1（2026-11-21，plugin 1.16.0）

起因：專案 README 改為 MD 與 HTML 雙軌並行——`README.md` 是文字精簡版，`README.html` 是完整的專案說明書。

| # | 變更 | 落點 |
|---|------|------|
| 1 | 新增工作 D「寫或更新 README」：兩份的定位、HTML 章節、撰寫規則、同步規則 | SKILL.md §1、§9 |
| 2 | 新增 `README.html` 範本：沿用維護者實際專案說明書的版面與三張圖（分層架構、資料交換、工作流程），內容換成佔位字 | `templates/README.html` |
| 3 | `README.md` 範本加一行指向 `README.html`，根目錄檔案列補上 `README.html` | `templates/README.md` |
| 4 | 建立新專案時一併複製 `README.html` | SKILL.md §2、§7 |

待辦：
- `README.html` 範本以無頭瀏覽器在深色模式、寬 1200 px 看過第 0–3 節與圖 A（版面正常）；
  圖 B、圖 C、第 5 節以後、淺色模式與列印只檢查了標籤成對與目錄節次一致，尚未實際檢視。

## v1.0（2026-11-21，plugin 1.15.0）

由維護者的 MATLAB / Simulink 專案範本（根目錄 `CLAUDE.md` 與 `README.md`）整理成 skill。
範本兩檔原樣收在 `templates/`，新專案複製後取代佔位字即可使用。

| 內容 | 落點 |
|---|---|
| 三種工作：建立新專案、歸類檔案、盤點既有專案 | SKILL.md §1 |
| 九個第 1 層資料夾、相依鏈與三條規則 | SKILL.md §2 |
| 模型放哪裡的三個問句 | SKILL.md §3 |
| 檔案歸類表；規則沒涵蓋時不自創資料夾 | SKILL.md §4 |
| `data\` 編排：分系統資料、整合測試階段 | SKILL.md §5 |
| 產出雙軌與命名 | SKILL.md §6 |
| 建立新專案的步驟 | SKILL.md §7 |
| 盤點表、搬移規則、已知的坑 | SKILL.md §8 |

範本以外、由實作經驗補上的內容：§8 的引用搜尋、搬移步驟與四個已知的坑；
§7 哪些資料夾上 project path。

待辦：
- 範本 `CLAUDE.md` §3、§4（撰碼準則與檔頭）與 `pxa-matlab-style` 內容重疊，
  且「既有檔案的引號是否統一改」兩處寫法不同，待維護者裁定以哪一份為準。
- 論文、規格書、第三方程式、停用檔案的位置範本未定。
