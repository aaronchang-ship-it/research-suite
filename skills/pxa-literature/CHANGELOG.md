# literature skill — CHANGELOG

## v3.4（2026-08-14）

命名規則化＋temp 入庫快速指令（依使用者四條規則）。

| # | 規則 | 落點 |
|---|------|------|
| 1 | atomic note 命名硬規則化：**一律英文原文術語**（不用中譯/自創簡稱；縮寫慣稱附括號） | SKILL.md §階段一-4 |
| 2 | source note 命名＝**`年份 作者.md`**（第一作者姓氏；同年同作者 a/b 消歧；完整標題住 frontmatter `title`；既有 vault 舊名沿用不改，避免斷鏈） | SKILL.md §階段一-3 |
| 3 | temp → source/ 搬移檔名＝**`年份 作者 完整標題.ext`**；新增快速指令「**入庫**」＋ `scripts/ingest.py`（模型抽 metadata 寫 manifest、腳本確定性去重比對＋清洗非法字元＋搬移改名；僅 NEW 搬移、DUP/SIMILAR 留 temp 不覆蓋） | SKILL.md §階段一-1b（新節）、scripts/ingest.py（新增） |
| 4 | 入庫差異回報用 **i-have-adhd 模式**（已安裝則呼叫 `i-have-adhd:i-have-adhd`；未安裝比照精神：結論先行、一表掃完、每檔一行「彌補了什麼/重疊在哪」） | SKILL.md §階段一-1b |

已測：ingest.py 三情境（精確重複 DUP-FILE、`&`/`and` 變體 SIMILAR 0.95 留裁定、全新 NEW 搬移改名）全數正確。

## v3.3.1（2026-08-13）

新增 **MOC 黃金範本** `references/example-MOC-golden.md`——v3.3 給了架構規格與模板（骨架），本版補血肉：自同一實戰知識庫挑六段原文＋逐段點評（好在哪、壞寫法長怎樣）＋句式速查表。涵蓋：設計情境表第三欄（參數→知識庫後果）、就緒度（行動指令而非自評分數）、領域定位（承上/拆內/啟下/對應一段完成）、適用性欄三段式（判斷＋原因＋補救）、SOTA 拆斷點（「只能回答 X、尚無法回答 Y」）、⟳ 追蹤（已補側/仍缺側各自點名）。SKILL.md §5 與 moc-architecture.md 加「動筆前先讀」指向（比照 example-atomic-note 慣例）。

## v3.3（2026-08-11）

固化**兩層式 MOC 架構**——自「25kg eVTOL 結構佈局知識庫」（總覽＋6 領域、55 篇文獻、120+ 筆記）實戰萃取，使用者評定該組 MOC 產出品質高，將其模式複製為本 skill 慣例。

| 項目 | 變更 | 落點 |
|------|------|------|
| 架構參考 | 新增 `references/moc-architecture.md`：兩層架構規格（總覽管跨、子 MOC 管深）、領域切分邏輯（邊界條件/輸入 → 核心方法/建模 → 材料/實作 → 應用域 → 進階/參考層）、七項品質機制 | references/（新增） |
| 模板 | 新增 `MOC-overview.md`（設計情境表、領域導覽含就緒度、全域推導鏈、逐 RQ SOTA、SP Roadmap 依就緒度排序）與 `MOC-domain.md`（領域定位、本情境適用性欄、⟳ 缺口追蹤） | templates/（新增 2 份） |
| 階段〇 | 新增「設計情境」項：具體參數表為所有萃取/比較/SOTA 判斷之錨 | SKILL.md §階段〇 |
| §5 改寫 | 單層 vs 兩層架構選擇（≳20 筆記或多領域 → 兩層）；比較矩陣加「本情境適用性」欄；SOTA 誠實分層（可落地/須限定/完全缺口）＋降級保留（監控/選配/參考層）；缺口 ⟳ 追蹤（部分已補不刪條目、「仍缺」給 scout 精確目標）；就緒度標注 | SKILL.md §階段一-5 |
| QA | W MOC 章節檢查改二擇一：總覽須「研究框架」、子 MOC 須「領域定位」；「待釐清」兩層皆必 | scripts/check_vault.py |

設計原則：範式的靈魂不在章節多，而在**設計情境錨定**（對著具體設計下結論，非泛泛綜述）與**誠實就緒度**（寧可標低不可虛胖）——這兩者是該知識庫品質高的根本原因。

## v3.2.1（2026-08-06）

修 bug：執行本 skill 時，`check_vault.py` 會被複製到使用者專案根（含 QA 輸出落地 vault_report.txt）。根因＝SKILL.md 指令用相對路徑 `scripts/…`，session cwd 在專案根、路徑不存在，模型遂「重建」腳本進專案。修法：新增「腳本執行慣例」——腳本一律 `python3 <skill根>/scripts/…` 從 skill 自身目錄執行、禁止複製進專案；QA 結果以對話回報、不落地專案根。全部指令範例同步改 `<skill根>` 前綴。（scout／scribe／standards 同型問題同批修正。）

## v3.2（2026-08-01）

導入 **PDF 分流閘門**——解決「來源 PDF 本質（文字型／掃描型）不可控，導致讀取路徑與 token 成本不一致」的問題。起因：一次對 600 頁 PDF 跑 literature，token 快速見底；根因是「文字層擷取 vs 影像渲染」交由模型臨場判斷，缺大檔章節鎖定，且公式視覺核對規則可能觸發全文渲染。

| 項目 | 變更 | 落點 |
|------|------|------|
| PDF 分流閘門 | 新增 `scripts/pdf_probe.py`：量測每頁文字層覆蓋率，確定性判定 `text`／`hybrid`／`scanned`＋`large`（>200 頁）旗標，輸出強制路由 manifest。優先 poppler、回退 pypdf；OCR 分支**委派官方 `pdf` skill**，不內建 OCR | scripts/pdf_probe.py（新增） |
| 前置閘門 | 盤點階段於 `check_vault` 之外加跑 `pdf_probe`，Pass 1／Pass 2 一律依 manifest 路由讀取，不自行改路 | SKILL.md §階段一-1、總流程、最小起步 |
| 公式渲染限縮 | 公式視覺核對從「凡含數學式頁面」限縮為「選定深讀章節內、當下要轉寫公式的那幾頁」，禁止為找公式而整份／整章渲染影像 | SKILL.md §階段一-3、環境需求表 |
| 大檔章節鎖定推廣 | triage「預估深讀範圍」的 >200 頁章節鎖定，從「教科書」推廣到 paper/thesis/report 等所有 `large` 檔 | SKILL.md §階段一-2/-3 |
| 成本控制原則 | 品質原則新增第 6 條：分流路由、文字層優先、影像最小化、大檔絕不整份深讀／渲染 | SKILL.md §品質原則 |
| 增量更新連動 | scout 回流新檔亦先過 `pdf_probe` 再走 Pass 1 | SKILL.md §增量更新 |

設計原則：把高成本決策（文字 vs 影像）從模型裁量收回為機械判定——來源本質不論為何，讀取路徑固定、成本可預期；同時保品質（掃描件不再被當文字層擷取產出亂碼）。

## v3.1（2026-07-30）

新增「工程實踐」章節（source note）——銜接文獻研究與工程實作（coding／Simulink modeling）。

| 項目 | 變更 | 落點 |
|------|------|------|
| 工程實踐章節 | source note 於「我的評註」後新增**必要**章節：實作標的／介面定義（維度、單位、來源式號）／逐步實驗步驟（帶錨點＋驗證點）；純文字描述、不畫圖；無可實作內容寫「不適用（原因）」（比照「爭議與歧異」的「無」模式） | SKILL.md §階段一-3、templates/source-note.md |
| 機械檢查 | E8 必要章節（sources）加入「工程實踐」 | scripts/check_vault.py |
| 階段二連動 | 「工程實踐」節彙整為工程文件「實作/驗證」章的素材 | SKILL.md §階段二-1 |
| evals | eval 0 expected_output 納入工程實踐；新增 eval 4（可實作文獻寫實作藍圖、survey 寫不適用） | evals/evals.json |
| 流程圖同步 | 階段一插入「工程實踐」節點（◆v3.1 標記）；階段二 MOC 節點加「工程實踐 → 實作/驗證章素材」；下游節點改「Python／Simulink／EXE」並列工程實踐為依據 | pipeline-flowchart.html |

設計原則：概念層演算法細節仍住原子筆記「演算法程序」，工程實踐是**文獻層級**的端到端實作藍圖，只引用不重複（一個概念一個家）。

## v3（2026-07-28）

依審查發現逐步更新（編號對應審查報告；v2 原版保留於 `.claude/skills/literature/`，本版位於專案根 `literature-v3/`，經審閱後手動取代原版即可生效）。

### 步驟 1 — 研究能力層（A1–A6）

| 審查項 | 變更 | 落點 |
|--------|------|------|
| A1 缺批判性評估 | source note 新增必要章節「批判評估」（evidence_level L1–L4、方法有效性、適用邊界、可信度評語）；frontmatter 加 `evidence_level`；階段二引用弱證據結論須如實限定效力 | SKILL.md §階段一-3、templates/source-note.md、check_vault E5/E8 |
| A2 文獻衝突無處理機制 | atomic note 新增**必要**章節「爭議與歧異」：歧異一律並陳＋錨點＋裁定（已裁定/未裁定），禁止默默擇一；未裁定項同步登錄 MOC 待釐清；無歧異須寫「無（已核對 N 份）」 | SKILL.md §階段一-4、templates/atomic-note.md、check_vault E8 |
| A3 非研究問題驅動 | 新增「階段〇：研究框架確認」（RQ、工程決策需求、萃取判準三判準）；atomic note frontmatter 加 `rq` | SKILL.md §階段〇、templates、check_vault E5 |
| A4 缺綜合層 | MOC 升級為「索引＋綜合層」：方法比較矩陣（欄位依決策需求）、SOTA 評述（逐 RQ）、待釐清升格必填且條目寫成 scout 缺口語句 | SKILL.md §階段一-5、templates/MOC.md、check_vault W(MOC) |
| A5 閱讀策略太薄 | 新增 Pass 1 全批略讀 → triage 表（seminal/derivative/survey、關聯 RQ、分群、優先序、深讀範圍）；深讀順序依 triage：survey 先、同群 seminal → derivative | SKILL.md §階段一-2 |
| A6 符號統一政策缺席 | 每主題建 `notes/{主題}-符號慣例.md`（軸系、正負號、無因次化）；原子筆記符號表改三欄：本筆記符號｜原文符號（各文獻）｜意義，不一致須寫轉換說明 | SKILL.md §階段一-4、templates/atomic-note.md |

### 步驟 2 — 品質保證層（B7–B10）

| 審查項 | 變更 | 落點 |
|--------|------|------|
| B7 萃取完整性無法驗證 | source note 新增「涵蓋自評」（章節/貢獻逐項標記已萃取/未萃取＋原因）；QA 內容抽驗加第三軌「完整性抽驗」（以涵蓋自評對照原文查 recall） | SKILL.md §階段一-3/-6、templates/source-note.md、check_vault E8 |
| B8 原子筆記無強制內容抽驗 | 含「數學形式」的原子筆記升 `stable` 前公式**全驗**（逐條對照頁面渲染影像），不適用抽驗率 | SKILL.md §階段一-6 |
| B9 status 純榮譽制 | frontmatter 加 `verified: none/structure/content`（＋`verified_date`）並與 status 機械綁定：`stable` 必須 `verified: content`（腳本強制）；stable 後實質修改 → 降回 draft 重驗 | SKILL.md §階段一-6、templates、check_vault E9 |
| B10 頁碼錨點無機械檢查 | check_vault 新增 E7：source note 重點摘錄與 atomic note 來源段每條 bullet 須含 p./§/Eq./ch./式 等錨點 | scripts/check_vault.py |

### 步驟 3 — 工程與腳本層（C11–C14）

| 審查項 | 變更 | 落點 |
|--------|------|------|
| C11 書目 metadata 太弱 | source note frontmatter 加 `venue`、`bibkey`（必填）與 `doi`、`volume_pages`（建議）；階段二參考文獻改由 frontmatter 機械生成，不憑記憶補書目 | templates/source-note.md、SKILL.md §階段二-1、check_vault E5/W |
| C12 check_vault.py 弱點 | (a) `source_file` 改相對路徑比對，同名檔強制完整路徑（E6）；(b) frontmatter 行尾註解只在「空白＋#」時剝除，含 `#` 的 title 不再截斷；(c) 孤兒檢查拆分：全無入鏈＝error、僅 MOC 入鏈＝warning（W1）；另新增 E8/E9/E10/W2 檢查與 error/warning 分級（warning 不擋 gate） | scripts/check_vault.py |
| C13 公式轉寫方法與風險不匹配 | 新增公式轉寫規則：文字層擷取僅作初稿，含數學式頁面須以頁面渲染影像視覺核對後才可寫入 | SKILL.md §階段一-3、環境需求表 |
| C14 增量更新無程序 | 新增「增量更新程序」：新文獻併入 triage → 整合進既有筆記（status 降級＋變更紀錄節）→ 連動 MOC/矩陣/開放問題 → 已交付文件列「受影響段落清單」交使用者決定 → 重跑 QA | SKILL.md §增量更新、templates/atomic-note.md |

### 步驟 4 — 其他（D15–D16）

| 審查項 | 變更 | 落點 |
|--------|------|------|
| D15 evals 覆蓋不足 | 新增 eval 2（衝突整合＋符號對映＋增量降級）、eval 3（QA 失敗修復，含「不可捏造頁碼」紅線）；原有 eval 0/1 的 expected_output 對齊 v3 產物 | evals/evals.json |
| D16 無人值守與大批量 | 新增專節：無人值守＝假設＋記錄＋待裁定清單（衝突一律不代裁）；>10 篇時 Pass 2 可分群平行，但整合/MOC/QA 必須單一主流程 | SKILL.md §無人值守與大批量模式 |

### 同步更新

- `pipeline-flowchart.html`：加入階段〇研究框架帶、triage 節點、批判評估＋涵蓋自評節點、MOC 綜合層節點、QA 三軌抽驗、status↔verified 綁定、增量更新帶、下游「MOC 開放問題 → scout」節點；v3 新增項以紫色 ◆v3 標示。
- `references/example-atomic-note.md`：對齊 v3 格式（`rq`/`verified` frontmatter、爭議與歧異節示範「無歧異」寫法、三欄符號表、證據層級限定語）。

### 未變更（刻意保留）

- `obsidian/` 資料夾命名慣例、三類筆記架構、公式與文本分離規則、階段推進確認、停止點、語言慣例——v2 的骨架全數保留，v3 只疊加研究判斷層與驗證強度。
