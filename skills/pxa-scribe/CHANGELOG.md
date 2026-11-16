# scribe skill — CHANGELOG

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
