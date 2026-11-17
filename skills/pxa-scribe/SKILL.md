---
name: pxa-scribe
description: 從 obsidian 知識庫（Obsidian vault）產出對標 NASA-TP 等級的 PXA 研究報告——先盤問清楚使用者要研究什麼（grill 模式，一次一題問到收斂），搜尋 vault 盤點素材就緒度，提出報告 roadmap，再逐章撰寫；前頁/STRN/審查格式遵循 pxa-standards 之 PXA-STD-SP 體系，內文架構對標 NASA Technical Publication。凡使用者提到寫 SP、寫報告、技術報告、研究報告、scribe、PXA-STRUCT-SP、Report.md、把 vault/筆記庫寫成報告、規劃報告 roadmap、想研究某題目要產報告——即使沒有明說 skill 名稱——都應使用本 skill。專案內有 Obsidian 知識庫時優先使用；找不到時改依專案資料夾編排規則找證據文件（如模組規格文件、PDF 原檔、測試資料，典型為模型驗證報告），仍找不到則先向使用者確認資料來源。範圍到 Report.md 定稿＋（使用者確認後）docx 轉檔為止；審查簽核（DAA）不在本 skill 範圍。
argument-hint: "[選填：研究題目或 STRN，如 機身佈局、PXA-STRUCT-SP-2026-002、續寫第 3 章]"
---

# scribe — 從 vault 產出 PXA 研究報告（NASA-TP 等級）v2.2

> 📊 本 skill 套件內附 `pipeline-flowchart.html`——整條 pipeline 的一頁式流程圖（尚未畫入 v2.1 的證據來源判定）。
> 🆕 v2.2：docx 版面改用 Word 範本 `templates/PXA-SP-template.dotx`（轉檔腳本每次先複製範本再套用；沒有 Claude 的同仁可直接用同一份範本手動編寫）。
> v2.1：證據來源判定——vault 優先；無 vault 時依專案資料夾編排規則找證據文件，找不到就問使用者。
> v2.0：grill 需求盤問前置、內文架構對標 NASA-TP、產出路徑 `documents/{STRN}.md` 平鋪、MD 永遠先行。

定位：**研究報告的主導者**，不只是格式執行者。工作次序固定為——**先了解使用者到底想研究什麼
（盤問）→ 判定證據來源並盤點手上有什麼（素材就緒度）→ 規劃報告 roadmap（交裁定）→ 撰寫**。
下文各步驟以 vault 用語書寫；走專案證據路徑時，「筆記」讀作「專案證據文件」，差異以步驟 1c 的表為準。
規則分工：**前頁、STRN、審查格式、[C-n]、語言規則照 PXA-STD-SP 體系（SSoT 在 pxa-standards）；
內文架構與寫作深度對標 NASA-TP**——動筆前先讀 `references/tp-writing-guide.md`（自 9 份 NTRS TP
實件萃取的架構與行文標竿）。

## 規則 SSoT（撰寫時隨用隨讀，不要憑記憶）

位置：同 plugin 內的 `pxa-standards` skill——路徑由 skill 系統定位，勿寫死安裝路徑。

| 文件 | 用途 | 何時讀 |
|------|------|--------|
| 本 skill `references/tp-writing-guide.md` | **內文架構與寫作標竿**（TP 骨架、五段式引言、論證密度、圖表/附錄慣例） | 立案時全讀；各章動筆前重讀對應節 |
| standards `references/PXA-STD-SP-002.md` §7.2（前頁模板）、§4（語言/引用/禁止用語）、§3.5（[C-n] 三要素）、§5（表格 Schema） | 前頁、審查格式與內容紀律 | 前頁與 Conclusions 動筆前；撰寫中隨用隨讀 |
| standards `references/PXA-STD-SP-001.md` | 治理：STRN（§3）、審查等級（§4）、文獻層級 §5.1、信度 ★ §5.2、vault 證據鏈 §5.5 | 遇疑義時查對應章節 |
| standards `references/writing-examples.md` | 句型庫與段落模式 | 各章動筆前 |
| `documents/SP-series-map.md` | 系列切分、素材清單、裁定紀錄 | 立案時；roadmap 更新時回寫 |

> 內文結構以 **TP 架構**為準——**已回寫 STD 正本**（裁定 #10，SP-002 v2.1 §3.0）：Part 1–6
> 僅強制於 TM/TP，SP（研究）依 TP 骨架；前頁/審查/[C-n]/語言照 STD。check_sp 已支援 TP 模式自動偵測。

## 執行流程

### 0. Grill — 需求盤問（動筆前，一次一題問到收斂）

比照 relentless-interview 模式：**每輪只問一題**，答案決定下一題，目的是把「想研究什麼」
磨到可立案的精度。典型追問鏈（依答案調整，不逐條照唸）：

1. **題目邊界**：你要研究的是什麼？一句話。（太寬→追問切哪一塊；太窄→確認夠不夠成一份報告）
2. **讀者與用途**：誰讀？拿來支撐什麼決策（選型？認證論據？團隊教材？）——決定深度與比較矩陣欄位。
3. **深度取捨**：要到「方法可重現」還是「結論可引用」？哪些部分可以只做綜述？
4. **邊界排除**：明確不做什麼（範圍蔓延是報告難產主因）。
5. **既有依賴**：與既有 SP／series-map 的關係（延伸？獨立？取代？）。

收斂判準：能寫出一行「本報告回答 X，供 Y 用於 Z，不含 W」即停。
使用者說「直接寫」或題目已明確（如給了 STRN）可跳過；無人值守時以合理假設續行並標注「未經確認」。

### 1. 證據來源判定與盤點（v2.1：vault 優先，找不到不硬套）

**1a. 判定證據來源——依序檢查，命中即停：**

| 順位 | 檢查 | 命中條件 | 走哪條路 |
|:---:|------|----------|----------|
| 1 | 專案路徑內有無 Obsidian 知識庫 | 有 `obsidian/`；或任一資料夾含 `.obsidian/`；或同層並存 `sources/`＋`notes/`＋`MOCs/` | **vault 路徑**（1b）——有 vault 一律優先用 |
| 2 | 專案的資料夾編排規則 | 專案 `CLAUDE.md`、`README.md` 的資料夾結構節、或聲明為「唯一真相」的規格文件，寫明了證據放在哪（如模組規格 md、`paper/`、`datasheet/`、`data/`、測試報告） | **專案證據路徑**（1c） |
| 3 | 以上皆無，或規則互相矛盾、指不到題目相關的資料 | — | **停下問使用者**：一題問清楚「這份報告的資料來源在哪」，取得答覆後走 1c |

- 不猜、不全碟搜尋；專案路徑以外的資料夾未經使用者同意不讀。
- 有 vault 但題目相關素材不足（搜不到對應 MOC／筆記）時**不自動改走 1c**：回報缺口，由使用者
  裁定「先 scout／literature 補 vault」或「缺口部分改用專案證據文件」（後者該部分依 1c 處理並標明）。
- 判定結果（走哪條路、依據哪份規則或使用者哪句話）寫進 roadmap，並回寫 `SP-series-map.md`（若有）。

**1b. vault 路徑——搜尋知識庫，回報就緒度：**

1. 以題目關鍵字搜 vault：對應 MOC（含兩層式的領域子 MOC）→ atomic notes → source notes。
2. 跑 literature 的 `check_vault.py`（結構須全過）；統計素材 status（`stable`／`reviewed`／`draft`）
   與 L2 文獻數（不足 5 依協調制回報裁量，STD-SP-001 §5.5）。
3. 產出**素材就緒度表**：章節構想｜可用筆記｜status 分佈｜缺口（缺口重的章節標明「需先 scout／
   或降級為綜述」）。MOC 的待釐清節與就緒度標注是現成輸入。

**1c. 專案證據路徑——無 vault 時（典型：模型驗證報告，證據是模組規格文件＋PDF 原檔＋測試資料）：**

1. 依 1a 找到的編排規則列出**證據來源表**交使用者確認：來源文件｜位置｜類型（規格文件／論文／
   規格書／測試資料／腳本）｜能支撐哪些章節｜可追溯到什麼（PDF 頁碼、資料檔＋腳本、日期）。
   使用者確認前不進 roadmap。
2. 產出**素材就緒度表**：章節構想｜可用文件與章節｜錨點是否齊全（有無頁碼／式號／資料檔）｜缺口。
   不跑 `check_vault.py`（無 vault 可檢）。
3. 本路徑的規則差異：

| 項目 | vault 路徑 | 專案證據路徑 |
|------|-----------|-------------|
| 追溯鏈 | 報告 → 原子筆記 → source note → PDF 頁碼 | 報告 → 專案證據文件（檔名＋章節）→ 原始檔（PDF 頁碼／資料檔＋產生它的腳本） |
| ✓／⚠ | 依 vault status 對映（stable→✓、reviewed→⚠） | 無 status 可對映，回到 STD-SP-001 §5.2 的本義：≥ 2 個獨立來源或方法交叉確認才標 ✓，否則 ⚠ |
| [C-n] ★ | status 決定上限 | 依 STD-SP-001 §5.2 信度判定樹逐條判定 |
| 數值與引文 | 當下回 vault → PDF 查核 | 當下回專案證據文件 → 原始檔查核；規格文件寫了但原始檔對不上者，以原始檔為準並回報 |
| References | 由 source notes frontmatter 機械生成 | 由規格文件的文獻節＋PDF 首頁書目資訊整理，逐筆對原檔；不憑記憶補作者、卷期、DOI |
| 發現來源有錯 | 先修 vault 再寫報告 | 回報使用者，依該專案的寫入規則先修來源文件再寫報告；禁止只在報告端修正 |
| 模型驗證結果 | — | 沿用來源文件的驗證性質標示（對量測／對規格書／自洽／退化一致，見 pxa-modeler）；**自洽與退化一致不得寫成驗證過實物**，未定驗收標準者照實寫 |

4. **偏離記錄（必要）**：STD-SP-001 §2.3／§5.5 現行條文規定 SP（研究）之證據必須可追溯至 vault。
   走本路徑即為偏離，須於書名頁背面寫明：證據基礎為何（列文件）、為何無 vault、本報告採用的
   追溯鏈。此項在標準修訂納入本路徑前不得省略。

### 2. Roadmap（交使用者裁定後才動筆）

產出報告 roadmap 交裁定：**STRN＋後綴**（`+v1-0+DRAFT`）、報告一行定位（步驟 0 的收斂句）、
**章節大綱**（依 tp-writing-guide 的 TP 骨架，逐章標素材來源與就緒度）、預估 [C-n] 方向、
缺口處置（先寫可寫的章 vs 先 scout）。多份報告時排序依就緒度（拉式），並回寫 `SP-series-map.md`。

### 3. 撰寫（逐章交審，不連寫多章）

**產出路徑（v2.0 硬規則）**：`documents/{STRN}.md`——專案 `documents/` 平鋪、STRN 為檔名。
**永遠 MD 先行**：全程只寫 MD；docx 是 MD 定稿後的轉檔動作，不在撰寫期考慮。

撰寫順序（TP 架構，成熟內容先寫）：

```
1.2 Literature review → 技術主體章（2..N，逐章）→ Conclusions
→ Introduction 其餘（1.1/1.3/1.4/1.5）→ Abstract（最後）
→ 前頁（STD-SP-002 §7.2）→ Nomenclature 整併 → References（機械生成）→ Appendix
```

各步要點：

- **Literature review（§1.2）**：依 L1/L2/L3 組織、現況→缺口→本報告定位；行文標 `[Author Year][L2]✓`。
  vault source notes「與主題關聯」段是現成素材。
- **技術主體章**：理論/建模→方法→應用/結果；每個方程標 `[Author Year, Eq.X]`（沿用筆記原文式號），
  公式五元素照 STD；假設 A-n 附合理性；每個技術主張落在推導/數據/引用三支撐之一
  （tp-writing-guide §二）；驗證比較須 ✓/⚠ 佐證；細節下放 Appendix、正文保持主線。
- **Nomenclature**：正文符號一律入表（符號/定義/單位），與 vault 符號慣例筆記對齊。
- **Conclusions**：逐條 `**[C-n]** ★ {結論}`＋適用條件＋限制——**缺適用條件即禁止發行**；
  ★ 依 STD-SP-001 §5.2（stable→上限★★；reviewed→★；⚠ 隨筆記帶出）。
- **Introduction 五段式**：Objectives 由研究框架 RQ 轉寫；Contributions 與 [C-n] 逐條對映。
- **Appendix**（含逐字摘錄附錄）：每筆正文引用附 verbatim 原文（回 `source/` PDF 擷取，非英文附英譯），
  禁止憑記憶或筆記轉述充當摘錄。
- **正式化書寫（SP-002 §4.1，v2.2）**：繁中優先、專有名詞首現「中文（English, 縮寫）」後沿用、
  標題雙語「中文（English）」（含五個 TP 必要節；check_sp 已容許）、補充說明以「須注意，……」等
  正式敘述句行文，禁括號夾註／口語附記；口吻依 tp-writing-guide §五。
- 素材為 `reviewed` 的內容降信度處理（⚠/★），`stable` 才標 ✓；References 由 source notes
  frontmatter（bibkey/authors/year/title/venue/doi）機械生成。

### 4. 合規 gate（MD 定稿前）

1. 執行 pxa-standards 的 `python3 <pxa-standards根>/scripts/check_sp.py documents/{STRN}.md`
   （從該 skill 目錄執行，不複製進專案）。**check_sp 已支援雙模式**（SP-002 v2.1 §8.1）：
   無 `## Part N:` 標題即自動走 TP 模式（檢 TP 骨架必要節、Abstract 淨空、逐字摘錄附錄），
   全部 [S] 項須全過——不再有豁免。
2. 人審清單（STD-SP-002 §8.2）逐項回報；逐字摘錄附錄抽驗 ≥20% 回 PDF 比對。
3. 對照 tp-writing-guide §四自查：完整自足、誠實邊界、結論可追溯。

### 5. MD 定稿 → （確認後才）docx

**使用者確認 MD 定稿後**，才執行轉檔：

```
python <skill根>/scripts/md2docx.py documents/{STRN}.md
```

腳本每次依序做三件事，不需另外下指令：

1. **先複製範本**：把 `<skill根>/templates/PXA-SP-template.dotx` 複製成暫存 docx，樣式、頁首頁尾、
   邊界都取自這份副本。
2. **轉檔**：pandoc 以該副本為樣式來源，把 MD 轉成 docx（公式轉為 Word 原生方程式）。
3. **套版面**：重排封面與書名頁、分三節編頁碼、調整表格、填入頁尾之報告編號與安全等級。

版面規格（由範本與腳本共同保證，撰寫時不必處理）：

| 項目 | 規格 |
|------|------|
| 字型與行距 | 中文標楷體、英數 Times New Roman、12 點、行距 1.5 倍、靠左、全文黑色 |
| 標題 | 章（`##`）12 點粗體、英文全大寫、自動換頁；節與小節 12 點粗體；標題上下不加線 |
| 頁碼 | 封面不編；書名頁起小寫羅馬數字（書名頁計為 i、不顯示）；第 1 章起阿拉伯數字自 1 起 |
| 頁尾 | 頁碼置中，下一行為「報告編號｜安全等級」 |
| 表格 | 全框線、表頭淺灰底；欄寬依內容分配；表頭與短欄置中；列不跨頁；跨頁重複表頭；表內文字無間距 |
| 表標題／圖標題 | 表標題在表上方、圖標題在圖下方，置中粗體 |

為了讓腳本認得出各部分，MD 須符合下列寫法（`templates/PXA-SP-template.md` 是可照抄的骨架）：

- 前頁依序為 `## 封面`、`## 書名頁`、`## 書名頁背面`…，兩節各有一個 `#` 標題與「項目｜內容」表；
  封面表含報告編號、版本、日期、狀態、安全等級，書名頁表含作者、專案、階段。
- 第 1 章標題以 `## 1.` 開頭；腳本以此為前頁與正文之分界。
- 表標題寫成表格正上方的一段「表 N　標題」；圖用 `![圖 N　標題](路徑)`。
- 章與章之間的 page-break div 可保留（Typora 用），轉檔時會移除，換頁由章標題樣式負責。

> 腳本與範本住本 skill 目錄（`<skill根>`），禁止複製進專案。轉出後以 Word 另存 PDF（或
> `soffice --headless --convert-to pdf`）產預覽，抽查封面、任一公式頁、任一跨頁表格、摘錄附錄。
> 版面問題改範本或腳本後重轉，禁止手工改 docx。內容修訂一律回 MD 重轉（**MD 是 SSoT**）。
> 紙本歸檔 LaTeX 版交 pxa-latexer。

**範本維護與人工使用**：

- 沒有 Claude 的同仁：直接取用 `templates/PXA-SP-template.dotx`，在 Word 以它開新文件，照範本
  最後一個附錄「範本使用說明」填寫。人工編寫的報告以該 docx 為正本，不受上述「禁止手工改 docx」限制
  （該限制只適用於由 MD 轉出的 docx）。
- 改樣式（字型、行距、框線、頁尾）：在 Word 開啟 .dotx 本身修改樣式後存檔。
- 改範本內的示範內容：改 `templates/PXA-SP-template.md`，再執行
  `python scripts/md2docx.py templates/PXA-SP-template.md -o templates/PXA-SP-template.dotx` 重建。
- 範本隨公開 repo 發佈，內容須去識別化：不得放入真實專案名稱、人名、數據與圖。

交付後停止：審查簽核（DAA）不在本 skill 範圍，不要主動接續。

## 合規紅線（時刻自查）

1. **禁止記憶引用**：數值/引文當下回證據來源（vault 或專案證據文件）→原始檔查核；查不到→定性陳述＋`[來源待補]`。
   證據來源依步驟 1a 判定，**不得因找不到 vault 就改用記憶或自行假設資料位置**。
2. **MD 永遠先行**：docx 只在 MD 定稿確認後產生；docx 非 SSoT，禁止直接改 docx。
3. [C-n] 缺適用條件＝禁止發行。
4. 產出只落 `documents/{STRN}.md`——不建子資料夾、不散落他處。
5. 三無句（無推導、無數據、無引用支撐）不寫進技術主體。
6. Typora 相容：`$$` 三行、page-break 只在章之間、MD 頭部 metadata 完整。
