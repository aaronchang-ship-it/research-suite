# scribe skill — CHANGELOG

## v2.2（2026-11-17，plugin 1.13.0）

起因：一份報告的 docx 經多次手動調整後版面失控，重新排版並由使用者自四個方案中選定 AFRL 風格
（方案 B）。本版把該版面固定成 Word 範本，轉檔腳本與人工編寫共用同一份。

| # | 變更 | 落點 |
|---|------|------|
| 1 | **新增 Word 範本** `PXA-SP-template.dotx`：標楷體＋Times New Roman 12 點、行距 1.5 倍、全文黑色、章標題不加線、全框線表格、頁尾「報告編號｜安全等級」；含封面至附錄之完整骨架與「範本使用說明」附錄，可不經 Claude 手動填寫 | `templates/PXA-SP-template.dotx` |
| 2 | 範本內容來源 MD（去識別化佔位字）與佔位圖 | `templates/PXA-SP-template.md`、`templates/fig-placeholder.png` |
| 3 | **md2docx.py 改寫**：每次先複製範本再轉檔；封面與書名頁依範本版式重排；分三節（封面不編頁碼／前頁小寫羅馬數字／正文阿拉伯數字自 1 起）；表格欄寬依內容分配、表頭與短欄置中、列不跨頁、跨頁重複表頭；「表 N」段落自動套 Table Caption；未引用之範本圖檔不留在輸出 | `scripts/md2docx.py` |
| 4 | md2docx.py 只用 Python 標準函式庫與 pandoc，不再呼叫 `zip`／`unzip`（Windows 可直接執行） | `scripts/md2docx.py` |
| 5 | page-break div 轉檔時移除，換頁改由章標題樣式負責；粗體標籤行（如 `**致謝**`）後接內文者保留換行 | `scripts/md2docx.py` |
| 6 | 移除舊樣式檔與其建置腳本（微軟正黑體、藍色標題之舊版面） | `templates/SP-reference.docx`、`scripts/build_reference.py` |
| 7 | 步驟 5 改寫：版面規格表、MD 寫法要求、範本維護與人工使用方式 | SKILL.md §5 |

已知限制：
- 表格欄寬依字數估算，不是實際排版量測；六欄以上之文字表仍可能偏擠。
- 含合併儲存格之表格不自動調欄寬。
- 無目錄、圖表目錄；圖表仍為全文流水號（標準未要求，未做）。
- 版面規格目前只寫在本 skill；PXA-STD-SP-002 尚未納入（需標準核准）。

## v2.1（2026-11-16，plugin 1.12.0）

起因：一份模型驗證報告在沒有 vault 的專案撰寫——證據是模組規格文件與 PDF 原檔。v2.0 假設
證據一律在 Obsidian 知識庫，該次只能臨場以書名頁背面的偏離聲明處理。本版給它一條正式路徑。

| # | 變更 | 落點 |
|---|------|------|
| 1 | **證據來源判定**（三順位，命中即停）：專案路徑內有 Obsidian 知識庫 → 優先用；無 → 依專案資料夾編排規則（`CLAUDE.md`、`README.md`、聲明為唯一真相的規格文件）找證據文件；仍無或矛盾 → 停下問使用者。不猜、不全碟搜尋 | SKILL.md §1a |
| 2 | 有 vault 但題目素材不足時不自動改路，回報缺口交使用者裁定 | SKILL.md §1a |
| 3 | **專案證據路徑**：證據來源表交確認、就緒度表、與 vault 路徑的差異表（追溯鏈、✓／⚠、★、查核、References、來源修正、模型驗證性質） | SKILL.md §1c |
| 4 | 走專案證據路徑須於書名頁背面寫偏離記錄（STD-SP-001 §2.3／§5.5 現行條文要求 vault） | SKILL.md §1c-4 |
| 5 | 紅線 1 改為「回證據來源→原始檔查核」，並禁止因找不到 vault 而改用記憶 | SKILL.md 紅線 |

待辦（需標準核准，不在本次範圍）：
- STD-SP-001 §2.3／§5.5 修訂，把專案證據路徑納入正本（新裁定），屆時偏離記錄可改為一般聲明。
- `pipeline-flowchart.html` 未畫入證據來源判定。
- `references/vault-mapping.md` 仍為 Part 編號舊版，未涵蓋專案證據路徑。

## v2.0.2（2026-08-19）

以使用者置入之 8 份國科會/科技部航太成果報告（`references/reports/`——飛控容錯、滾轉飛彈複合控制、攔截導控、液態/混合火箭、高攻角實驗；即目標實驗室群實際行文）重寫 tp-writing-guide §五：口吻規則逐條改為**實件原文錨定**——「所＋V＋之」產物指稱句構、雙語首現母本（FCC/FBW/SMC）、目的＋文獻依據＋動作的方法句、「模擬結果顯示…能有效…」結果句、頓號特性列舉、爆炸事故誠實揭露範式、r6 摘要密度標竿。standards writing-examples.md 同步新增 §5 繁中句型庫（v1.1）。

## v2.0.1（2026-08-18）

配合裁定 #11（SP-002 v2.2 正式化書寫規範）：tp-writing-guide 新增 §五「繁體中文正式書寫口吻」（自稱/語態、慣用句式表、譯名判準、避免清單——標竿為台灣學位論文與政府科技報告通行書面語）；SKILL.md 撰寫要點增列正式化書寫條目；check_sp TP 必要節已容許「中文（English）」雙語標題，中文優先可貫徹全文。

## v2.0（2026-08-16）

依使用者實戰心得重定位：從「格式合規的執行者」改為「**研究報告的主導者**」，對標 NASA-TP 等級。

| # | 變更 | 落點 |
|---|------|------|
| 1 | **Grill 需求盤問前置**（比照 mattpocock grill-with-docs 精神）：一次一題問到收斂（題目邊界→讀者用途→深度→排除→依賴），收斂判準＝能寫出「本報告回答 X，供 Y 用於 Z，不含 W」；可跳過、無人值守自動改假設模式 | SKILL.md §0 |
| 2 | **Vault 盤點＋Roadmap**：搜 MOC/notes 產素材就緒度表 → 章節大綱逐章標素材與缺口 → 交裁定才動筆；多報告依就緒度排序（拉式） | SKILL.md §1–2 |
| 3 | **內文架構對標 NASA-TP**：新增 `references/tp-writing-guide.md`（自 temp/nasa-tp 9 份 NTRS TP 實件萃取：TP 骨架、Nomenclature 必要節、Introduction 五段式、漏斗式行文、三支撐論證密度、圖表/附錄慣例、深度標竿）；**前頁/STRN/審查/[C-n]/語言仍照 PXA-STD**（混合體系，使用者裁定）；check_sp 結構類 [S] 項與 TP 架構衝突者標「TP 架構豁免」待 standards 修訂同步 | references/（新增）、SKILL.md |
| 4 | **產出路徑規則化**：`documents/{STRN}.md` 平鋪（取消 report/ 子層）；**永遠 MD 先行**——docx 僅在使用者確認 MD 定稿後轉檔，紅線明文 | SKILL.md §3/§5、紅線 |
| 3b | **豁免已回寫正本（同日）**：裁定 #10 落 SP-002 v2.1（§3.0 SP 改依 TP 骨架、§8.1 雙模式）；check_sp.py 支援 Part/TP 自動偵測——scribe 不再有「TP 架構豁免」，全部 [S] 項須全過 | pxa-standards |
| 5 | TP 範例 PDF 不入庫（66MB 拖慢 plugin 同步），留 temp/nasa-tp 供日後參考；風格已萃取進 guide | —— |

舊版 vault 素材對應表（Part 編號版）內聯精簡進 SKILL.md；`references/vault-mapping.md` 保留供對照，隨 standards 修訂一併整理。
