#!/usr/bin/env python3
"""PXA 技術報告 Report.md 合規檢查（合規 gate）

用法:
    python check_sp.py <Report.md>

依 PXA-STD-SP-001 v4.0／PXA-STD-SP-002 v3.0 §8.1。所有技術報告共用 TP 骨架，
以 MD 頭部之「報告性質」（研究／設計／測試，可用＋並列）決定必要章節。

檢查項:
  1. 骨架必要節：摘要、緒論、結論；有 $$ 公式須有符號表；有 [Author Year] 引用須有參考文獻
     （容許「中文（English）」雙語標題）
  2. 報告性質已宣告，且其必要章節存在（章節標題關鍵字；多重性質取聯集）
  3. 章（##）之間有 page-break div；節（###）之前不得有
  4. $$ 三行格式（$$ 必須獨立成行）
  5. [C-n] 三要素：結論行含 ★/⚠ 信度標記，其後含「適用條件」與「限制」
  6. 禁止用語掃描（大約/應該可以/眾所周知/顯然/等等/顯著影響/大幅提升）
  7. 摘要淨空：無 $$ 公式、無 [Author Year] 外部引用
  8. 有外部引用時逐字摘錄附錄存在，且每個引用代碼有「引用摘錄」表
  9. MD 頭部 metadata：文件編號/版本/日期/狀態/報告性質 齊全
 10. [回報不擋件] [L2] 標記計數（協調制門檻 5）

仍含 `## Part N:` 標題者為舊制結構（SP-002 v3.0 起退役），判為不合規。

結束碼: 0 = 全過（第 10 項僅回報）, 1 = 有違規
"""
import re
import sys

BANNED = ["大約", "應該可以", "眾所周知", "顯然", "等等", "顯著影響", "大幅提升"]
PAGEBREAK = 'page-break-after: always'
CITE = r"\[[A-Z][A-Za-z&.\- ]+ (19|20)\d\d"

SKELETON = [("摘要（Abstract）", r"Abstract\b|摘要"),
            ("緒論（Introduction）", r"Introduction\b|緒論|引言"),
            ("結論（Conclusions）", r"Conclusions|Concluding Remarks|結論")]
NOMEN = r"Nomenclature\b|符號表|符號說明"
REFS = r"References\b|參考文獻"

# SP-002 §8.1 檢查項 2：必要章節 → 標題關鍵字
NATURE_SECTIONS = {
    "研究": [("文獻回顧", r"文獻回顧|Literature Review"),
             ("理論與建模", r"理論|建模|模型|方法|Theory|Model|Method")],
    "設計": [("理論與建模", r"理論|建模|模型|方法|Theory|Model|Method"),
             ("需求與設計基線", r"需求|設計基線|約束|Requirement|Baseline")],
    "測試": [("測試項目與通過準則", r"測試項目|通過準則|評估指標|Test Item|Acceptance|Metrics"),
             ("測試組態", r"組態|測試資料|測試設置|Configuration|Test Data|Setup"),
             ("偏差紀錄", r"偏差|Deviation")],
}


def main(path):
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    problems, notices = [], []

    # 標題清單（略過程式碼區塊內之 #）
    heads, fenced = [], False
    for i, l in enumerate(lines):
        if l.strip().startswith("```"):
            fenced = not fenced
        elif not fenced and re.match(r"^#{1,4}\s", l):
            heads.append((i, l))
    titles = "\n".join(l for _, l in heads)

    def has(pat):
        return bool(re.search(pat, titles))

    if re.search(r"^##\s*Part\s+\d", titles, re.M):
        problems.append("[結構] 含 `## Part N:` 標題——Part 1–6 為舊制結構，已退役；請改為 TP 骨架（SP-002 §3.0）")

    # 1. skeleton
    for name, pat in SKELETON:
        if not has(pat):
            problems.append(f"[結構] 缺必要節「{name}」")
    if "$$" in text and not has(NOMEN):
        problems.append("[結構] 有公式但缺「符號表（Nomenclature）」")
    cited = bool(re.search(CITE, text))
    if cited and not has(REFS):
        problems.append("[結構] 有外部引用但缺「參考文獻（References）」")
    if not any(re.match(r"^##\s*1\s*[\.．]", l) for _, l in heads):
        problems.append("[結構] 找不到以 `## 1.` 開頭之第 1 章（前頁與本文之分界）")

    # 9 + 2. metadata and report nature
    head = "\n".join(lines[:30])
    for field in ["文件編號", "版本", "日期", "狀態", "報告性質"]:
        if field not in head:
            problems.append(f"[metadata] 頭部缺「{field}」")
    m = re.search(r"報告性質[:：]\*{0,2}\s*([^\n]+)", head)
    natures = [n for n in NATURE_SECTIONS if m and n in m.group(1)]
    if m and not natures:
        problems.append(f"[性質] 報告性質「{m.group(1).strip()}」無法辨識（須為 研究／設計／測試，可用＋並列）")
    notices.append(f"[性質] {'＋'.join(natures) if natures else '未宣告'}")
    seen = set()
    for n in natures:
        for name, pat in NATURE_SECTIONS[n]:
            if name not in seen and not has(pat):
                problems.append(f"[性質/{n}] 缺必要章節「{name}」（標題須含：{pat.replace('|', '、')}）")
            seen.add(name)

    # 3. page breaks: between chapters yes, before sections no
    chapters = [i for i, l in heads if re.match(r"^##\s", l)]
    for a, b in zip(chapters, chapters[1:]):
        if PAGEBREAK not in "\n".join(lines[a:b]):
            problems.append(f"[分頁] 「{lines[a].strip()[:30]}」與下一章之間缺 page-break div")
    for i, l in enumerate(lines):
        if PAGEBREAK in l:
            nxt = next((x for x in lines[i + 1:i + 5] if x.strip() and x.strip() != "---"), "")
            if re.match(r"^###+\s", nxt):
                problems.append(f"[分頁] 第 {i+1} 行 page-break 出現在節之前（僅允許章之間）")

    # 4. $$ three-line format
    for i, l in enumerate(lines):
        s = l.strip()
        if "$$" in s and s != "$$":
            problems.append(f"[公式] 第 {i+1} 行 $$ 未獨立成行: {s[:60]}")

    # 5. [C-n] triples
    cns = [(i, l) for i, l in enumerate(lines) if re.match(r"^\*\*\[C-\d+\]\*\*", l.strip())]
    for i, l in cns:
        if not re.search(r"[★⚠]", l):
            problems.append(f"[C-n] 第 {i+1} 行缺信度標記（★/⚠）: {l.strip()[:50]}")
        block = "\n".join(lines[i:i + 6])
        if "適用條件" not in block:
            problems.append(f"[C-n] 第 {i+1} 行 {l.strip()[:20]} 缺「適用條件」（缺適用條件禁止發行）")
        if "限制" not in block:
            problems.append(f"[C-n] 第 {i+1} 行 {l.strip()[:20]} 缺「限制」")
    if not cns:
        problems.append("[C-n] 全文未找到任何 **[C-n]** 結論")

    # 6. banned phrases
    for w in BANNED:
        for i, l in enumerate(lines):
            if w in l and not l.strip().startswith(">"):
                problems.append(f"[用語] 第 {i+1} 行含禁止用語「{w}」")
                break  # 每詞回報一次即可

    # 7. abstract clean
    m = re.search(r"^##[^\n]*(?:Abstract\b|摘要)[^\n]*$(.*?)^##\s", text, re.M | re.S)
    if m:
        if "$$" in m.group(1):
            problems.append("[摘要] 含公式（禁止）")
        if re.search(CITE, m.group(1)):
            problems.append("[摘要] 含外部文獻引用（禁止）")

    # 8. verbatim excerpts appendix
    if cited:
        app = re.search(r"^#+\s*(Appendix|附錄)\s*[A-Z]", text, re.M)
        if not app or not re.search(r"引用摘錄|逐字摘錄|Verbatim", text[app.start():]):
            problems.append("[附錄] 有外部引用但缺逐字摘錄附錄（SP-002 §6、§5.9）")
        else:
            appe = text[app.start():]
            for c in re.findall(r"^####\s*\[(.+?)\]", appe, re.M):
                seg = appe.split(f"[{c}]", 1)[1][:1500]
                if "引用摘錄" not in seg:
                    problems.append(f"[附錄] [{c}] 缺引用摘錄表")

    # 10. L2 count (report only)
    l2 = len(re.findall(r"\[L2\]", text))
    notices.append(f"[L2] 標記出現 {l2} 次（研究性質之協調制參考門檻 5；不足時須經使用者裁量）")

    print(f"=== check_sp: {path} ===")
    for n in notices:
        print("ℹ", n)
    if problems:
        print(f"\n=== 發現 {len(problems)} 項違規 ===")
        for p in problems:
            print(" ✗", p)
        sys.exit(1)
    print("\n=== 全數通過 ===")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
