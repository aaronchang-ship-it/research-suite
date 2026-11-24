#!/usr/bin/env python3
"""PXA 報告 MD → docx 轉換（scribe 交付管線，版面＝templates/PXA-SP-template.dotx）

用法:
    python md2docx.py <Report.md> [-o out.docx] [--template PXA-SP-template.dotx] [--no-xref]

流程（確定性，同一輸入產出同一版面）:
  0. 先複製範本（.dotx → 暫存 .docx），之後一切樣式、頁首頁尾、邊界都取自這份副本
  1. 前處理 MD：
     - 剝除 MD 頭部 metadata 區塊（docx 自「封面」起始）
     - 移除 page-break div 與其後緊鄰之 `---`（章標題樣式本身即「段落前分頁」）
     - 提示區塊 `> [!NOTE]` / `[!IMPORTANT]` / `[!TIP]` → 樣式化引用區塊；一般 `>` 區塊 → 內文段落
     - 粗體標籤行（如 **致謝**）後接內文者保留換行
     - `$$` 區塊內 \\tag{X} → 式尾 (X)
     - 移除審核標記 [L1]–[L4] 與其後之 ✓／⚠、證據層級說明句、Typora 目錄標記 [[TOC]]
     - 交互參照（docx_xref.md_pass）：引用、參考文獻、表／圖題注換成記號；--no-xref 或輸出 .dotx 時不做
  2. pandoc -t docx --reference-doc <範本副本>（LaTeX 數學 → Word 原生方程式）
  2a. 記號 → 欄位與書籤（docx_xref.docx_pass）：編號引用 [n]、SEQ 題注、REF 交互參照
  3. 後處理 docx：
     - 封面、書名頁依範本版式重排（資料取自 MD「封面」「書名頁」兩節之表格）
     - 分三節：封面不編頁碼｜前頁小寫羅馬數字（書名頁計為 i、不顯示）｜正文阿拉伯數字自 1 起
     - 表格：欄寬依內容分配、表頭與短欄置中、垂直置中、列不跨頁、跨頁重複表頭；
       表內段落套「無間距」；表前之「表 N」段落套 Table Caption
     - 頁尾之〔報告編號〕〔安全等級〕佔位字替換

只用 Python 標準函式庫與 pandoc；輸出副檔名為 .dotx 時寫成 Word 範本（維護範本用）。
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.dom.minidom as minidom
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docx_xref  # noqa: E402  同資料夾

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, '..', 'templates', 'PXA-SP-template.dotx')
CT_DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'
CT_DOTX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml'
CALLOUT = {'NOTE': 'NOTE', 'IMPORTANT': 'IMPORTANT', 'TIP': 'TIP'}

TBL = r'<w:tbl>.*?</w:tbl>'
ROW = r'<w:tr(?: [^>]*)?>.*?</w:tr>'
CELL = r'<w:tc>.*?</w:tc>'
PARA = r'<w:p(?: [^>]*)?>(?:(?!</w:p>).)*?</w:p>'
BLOCK = TBL + r'|<w:p(?: [^>]*)?>.*?</w:p>|<w:p/>'
CAPTION = r'\s*(表|Table)\s*[A-Z]?\d'
EM = 240           # 12 pt，單位 twip
PADX = 300         # 儲存格左右邊界加安全量


# ------------------------------------------------------------------ 前處理
def fix_tags(text):
    r"""$$ 區塊內 \tag{X} → 式尾 \qquad(\text{X})；pandoc 會丟棄 \tag，式號須保留供內文引用。"""
    def repl(m):
        body = m.group(1)
        tm = re.search(r'\\tag\{([^}]*)\}', body)
        if not tm:
            return m.group(0)
        body = re.sub(r'\s*\\tag\{[^}]*\}\s*', '\n', body).strip()
        return '$$\n' + body + '\\qquad(\\text{' + tm.group(1) + '})\n$$'
    return re.sub(r'\$\$\n(.*?)\$\$', repl, text, flags=re.S)


EVIDENCE = re.compile(r'證據層級|\[L#\]|依作者年份排序')       # 只對審查者有意義的說明（docx 改為編號排序）
MARK = re.compile(r'\[L[1-4]\][✓⚠]?')


def drop_evidence(line):
    """刪去含證據層級說明之子句（以頂層「，；」切分，括號內不切）；整句都是說明則整句刪去。"""
    out = []
    for sent in re.findall(r'[^。]*。?', line):
        if not EVIDENCE.search(sent):
            out.append(sent)
            continue
        pieces, depth, cur = [], 0, ''
        for ch in sent:
            depth += ch in '（(' and 1 or (ch in '）)' and -1 or 0)
            cur += ch
            if depth == 0 and ch in '，；':
                pieces.append(cur)
                cur = ''
        pieces.append(cur)
        keep = [p for p in pieces if not EVIDENCE.search(p)]
        if keep:
            s = ''.join(keep)
            out.append(s[:-1] + '。' if s[-1:] in '，；' else s)
    return ''.join(out)


def preprocess(text):
    m = re.search(r'文件編號[:：]\*{0,2}\s*([A-Za-z0-9+\-]+)', text)
    strn = m.group(1) if m else ''
    i = text.find('## 封面')
    if i > 0:
        text = text[i:]
    text = fix_tags(text)

    out, skip_hr, callout, fenced = [], False, False, False
    lines = text.split('\n')
    for k, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith('```'):
            fenced = not fenced
        if not fenced:
            if s in ('[[TOC]]', '[TOC]'):                                  # Typora 目錄標記
                continue
            if s and not s.startswith(('|', '#')) and EVIDENCE.search(s):
                ln = drop_evidence(ln)
                if not ln.strip():
                    continue
                s = ln.strip()
            ln = MARK.sub('', ln)
            s = ln.strip()
            if s.startswith('>') and not re.match(r'>\s*\[!', s):
                if not callout:                                          # 一般引用區塊 → 內文段落
                    ln = s[1:].lstrip()
                    s = ln
            callout = (callout and s.startswith('>')) or bool(re.match(r'>\s*\[!', s))
        if re.fullmatch(r'\*\*[^*|]+\*\*', s) and k + 1 < len(lines) and re.match(r'[^\s|#>$<\-*]', lines[k + 1]):
            ln = s + '\\'                                            # 粗體標籤行後接內文：保留換行
        if s.startswith('<div') and 'page-break-after' in s:
            skip_hr = True
            continue
        if skip_hr:
            if s == '':
                continue
            skip_hr = False
            if s == '---':
                continue
        # 清單項內縮排表格 → 提為頂層表格（pandoc 不解析巢狀縮排表）
        if re.match(r'^ {2,3}\|', ln):
            if out and out[-1].strip() != '' and not out[-1].lstrip().startswith('|'):
                out.append('')
            out.append(ln.lstrip())
            continue
        mm = re.match(r'>\s*\[!(NOTE|IMPORTANT|TIP)\]\s*(.*)', s)
        if mm:
            rest = mm.group(2).strip().strip('*').strip()
            tag = CALLOUT[mm.group(1)]
            out.append('> ' + ('**%s**' % tag if not rest else '**%s｜%s**' % (tag, rest)))
            continue
        out.append(ln)
    return '\n'.join(out), strn


# ------------------------------------------------------------------ 套件讀寫
def read_pkg(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist() if not n.endswith('/')}


def write_pkg(path, parts, as_template=False):
    ct = parts['[Content_Types].xml'].decode('utf-8')
    ct = ct.replace(CT_DOTX, CT_DOCX)
    if as_template:
        ct = ct.replace(CT_DOCX, CT_DOTX)
    parts = dict(parts)
    parts['[Content_Types].xml'] = ct.encode('utf-8')
    if os.path.exists(path):
        os.remove(path)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in ['[Content_Types].xml'] + [n for n in parts if n != '[Content_Types].xml']:
            z.writestr(name, parts[name])


# ------------------------------------------------------------------ XML 小工具
def plain(x):
    x = re.sub(r'<w:instrText[^>]*>[^<]*</w:instrText>', '', x)             # 欄位代碼不算顯示文字
    return html.unescape(re.sub(r'<[^>]+>', '', x)).strip()


def rows_of(tbl):
    return [[plain(c) for c in re.findall(CELL, r, flags=re.S)] for r in re.findall(ROW, tbl, flags=re.S)]


def pstyle(p):
    m = re.search(r'<w:pStyle w:val="([^"]+)"/>', p[:600])
    return m.group(1) if m else ''


def set_pstyle(p, sid):
    tag = '<w:pStyle w:val="%s"/>' % sid
    if '<w:pStyle ' in p[:600]:
        return re.sub(r'<w:pStyle w:val="[^"]+"/>', tag, p, count=1)
    if '<w:pPr>' in p[:300]:
        return p.replace('<w:pPr>', '<w:pPr>' + tag, 1)
    return re.sub(r'(<w:p(?: [^>]*)?>)', r'\g<1><w:pPr>' + tag + '</w:pPr>', p, count=1)


def space_before(p, twips):
    m = re.search(r'<w:pPr>.*?</w:pPr>', p, flags=re.S)
    xml = '<w:spacing w:before="%d"/>' % twips
    if not m:
        return re.sub(r'(<w:p(?: [^>]*)?>)', r'\g<1><w:pPr>' + xml + '</w:pPr>', p, count=1)
    ppr = m.group(0)
    if '<w:spacing ' in ppr:
        return p
    for anchor in ('</w:numPr>', r'<w:pStyle w:val="[^"]+"/>', '<w:pPr>'):
        a = re.search(anchor, ppr)
        if a:
            ppr = ppr[:a.end()] + xml + ppr[a.end():]
            break
    return p[:m.start()] + ppr + p[m.end():]


class Fmt:
    """版面常數：樣式 id 由範本之樣式名稱查得，版心寬由節屬性算得。"""

    def __init__(self, styles, sect):
        names = {n.lower(): i for i, n in re.findall(r'w:styleId="([^"]+)"[^>]*>\s*<w:name w:val="([^"]+)"', styles)}
        self.nosp = names.get('no spacing', 'Compact')
        self.h1 = names.get('heading 1', 'Heading1')
        self.h2 = names.get('heading 2', 'Heading2')
        self.heads = {names.get('heading %d' % k, 'Heading%d' % k) for k in range(1, 7)}
        self.tcap = names.get('table caption', 'TableCaption')
        pg = re.search(r'<w:pgSz [^>]*/>', sect)
        mar = re.search(r'<w:pgMar [^>]*/>', sect)
        w = int(re.search(r'w:w="(\d+)"', pg.group(0)).group(1)) if pg else 11906
        left = int(re.search(r'w:left="(\d+)"', mar.group(0)).group(1)) if mar else 1701
        right = int(re.search(r'w:right="(\d+)"', mar.group(0)).group(1)) if mar else 1417
        self.text_w = w - left - right

    # ---- 段落、表格產生器（封面、書名頁用）
    def run(self, text, size=24, bold=False, caps=False):
        rp = '<w:rFonts w:hint="eastAsia"/>'
        if bold:
            rp += '<w:b/><w:bCs/>'
        if caps:
            rp += '<w:caps/>'
        rp += '<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (size, size)
        return '<w:r><w:rPr>%s</w:rPr><w:t xml:space="preserve">%s</w:t></w:r>' % (rp, escape(text))

    def para(self, runs, jc='left', before=0, after=0, line=240, border=''):
        if isinstance(runs, str):
            runs = [runs]
        return ('<w:p><w:pPr><w:pStyle w:val="%s"/>%s<w:spacing w:before="%d" w:after="%d" w:line="%d" '
                'w:lineRule="auto"/><w:jc w:val="%s"/></w:pPr>%s</w:p>') % (self.nosp, border, before, after, line, jc, ''.join(runs))

    def grid_table(self, rows, widths, header):
        e = '<w:%s w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        out = ('<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>%s</w:tblBorders>'
               '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="50" w:type="dxa"/><w:left w:w="100" w:type="dxa"/>'
               '<w:bottom w:w="50" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>%s</w:tblGrid>'
               ) % (sum(widths), ''.join(e % s for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV')),
                    ''.join('<w:gridCol w:w="%d"/>' % w for w in widths))
        for ri, r in enumerate([header] + rows):
            out += '<w:tr><w:trPr><w:cantSplit/></w:trPr>'
            for ci, (c, w) in enumerate(zip(r, widths)):
                tcp = '<w:tcW w:w="%d" w:type="dxa"/>' % w
                if ri == 0:
                    tcp += '<w:shd w:val="clear" w:color="auto" w:fill="D9D9D9"/>'
                tcp += '<w:vAlign w:val="center"/>'
                out += '<w:tc><w:tcPr>%s</w:tcPr>%s</w:tc>' % (tcp, self.para(self.run(c, 24, ri == 0 or ci == 0),
                                                                              'center' if ri == 0 else 'left'))
            out += '</w:tr>'
        return out + '</w:tbl>'


BOX = ('<w:pBdr>' + ''.join('<w:%s w:val="single" w:sz="6" w:space="6" w:color="000000"/>' % s
                            for s in ('top', 'left', 'bottom', 'right')) + '</w:pBdr>')


# ------------------------------------------------------------------ 表格
def text_w(t):
    """估算排版寬度（twip）：全形字 1 em，其餘 0.58 em。"""
    return sum(EM if ord(ch) > 0x2E7F else EM * 0.58 for ch in t)


def bold_cell(c):
    def fix(m):
        r = m.group(0)
        if '<w:b/>' in r:
            return r
        if '<w:rPr>' in r:
            if re.search(r'<w:rPr><w:rFonts [^>]*/>', r):
                return re.sub(r'(<w:rPr><w:rFonts [^>]*/>)', r'\g<1><w:b/><w:bCs/>', r, count=1)
            return r.replace('<w:rPr>', '<w:rPr><w:b/><w:bCs/>', 1)
        return re.sub(r'(<w:r(?: [^>]*)?>)', r'\g<1><w:rPr><w:b/><w:bCs/></w:rPr>', r, count=1)
    return re.sub(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>', fix, c, flags=re.S)


def cell_par(p, f, jc, keep):
    """表內段落：無間距樣式，只保留清單編號與段落記號之字元格式。"""
    m = re.search(r'<w:pPr>(.*?)</w:pPr>', p, flags=re.S)
    old = m.group(1) if m else ''
    num = re.search(r'<w:numPr>.*?</w:numPr>', old, flags=re.S)
    rpr = re.search(r'<w:rPr>.*?</w:rPr>', old, flags=re.S)
    was = re.search(r'<w:jc w:val="(right|end|center)"/>', old)
    if jc == 'left' and was:
        jc = was.group(1)                                            # MD 明訂之靠右／置中予以保留
    new = ('<w:pPr><w:pStyle w:val="%s"/>%s%s<w:jc w:val="%s"/>%s</w:pPr>'
           % (f.nosp, '<w:keepNext/>' if keep else '', num.group(0) if num else '', jc, rpr.group(0) if rpr else ''))
    if m:
        return p[:m.start()] + new + p[m.end():]
    return re.sub(r'(<w:p(?: [^>]*)?>)', lambda g: g.group(1) + new, p, count=1)


def auto_widths(cells, ncol, text_w_total, has_header):
    cmax, cmin, bmax, oneline = [0] * ncol, [0] * ncol, [0] * ncol, [True] * ncol
    for ri, r in enumerate(cells):
        body_row = not (ri == 0 and has_header)
        for i, c in enumerate(r):
            ps = [plain(p) for p in re.findall(PARA, c, flags=re.S)]
            if body_row and len([p for p in ps if p]) > 1:
                oneline[i] = False
            for p in ps:
                cmax[i] = max(cmax[i], text_w(p) + PADX)
                if body_row:
                    bmax[i] = max(bmax[i], text_w(p) + PADX)
                tok = 0
                for t in re.split(r'\s+', p):
                    latin = re.findall(r'[^⺀-￿]+', t)                 # 中日韓文字可在任意處折行
                    tok = max([tok] + [text_w(x) for x in latin] + ([2 * EM] if len(''.join(latin)) < len(t) else []))
                if ri == 0 and has_header:
                    tok = text_w(p) * 1.12                           # 表頭（粗體）維持單行
                cmin[i] = max(cmin[i], min(tok + PADX, 0.34 * text_w_total))
    cmin = [max(m, 2 * EM + PADX) for m in cmin]
    cmax = [max(a, b) for a, b in zip(cmax, cmin)]
    if sum(cmax) <= text_w_total:
        if sum(cmax) * 1.12 < 0.72 * text_w_total:
            widths = [x * 1.12 for x in cmax]                        # 內容少：合身寬度並置中
        else:
            extra = text_w_total - sum(cmax)
            widths = [x + extra * x / sum(cmax) for x in cmax]
    elif sum(cmin) >= text_w_total:
        widths = [x * text_w_total / sum(cmin) for x in cmin]
    else:
        # 先滿足需求小的欄，長文字欄均分剩餘寬度
        widths = list(cmin)
        rem = text_w_total - sum(cmin)
        need = [a - b for a, b in zip(cmax, cmin)]
        todo = [i for i in range(ncol) if need[i] > 0]
        while todo and rem > 1:
            share = rem / len(todo)
            done = [i for i in todo if need[i] <= share]
            if not done:
                for i in todo:
                    widths[i] += share
                break
            for i in done:
                widths[i] += need[i]
                rem -= need[i]
                todo.remove(i)
    centre = [oneline[i] and bmax[i] <= 7 * EM + PADX for i in range(ncol)]      # 短欄（代號、數值、單位）置中
    return [int(round(x)) for x in widths], centre


def fmt_table(tbl, f, fracs=None, kv=False, pad=None):
    """fracs=None：欄寬依內容；否則依比例（前頁之欄位表）。kv：首欄粗體、§ 列合併成區段列。"""
    rows = re.findall(ROW, tbl, flags=re.S)
    cells = [re.findall(CELL, r, flags=re.S) for r in rows]
    ncol = len(re.findall(r'<w:gridCol ', tbl))
    regular = bool(rows) and ncol > 0 and all(len(c) == ncol for c in cells) and 'w:gridSpan' not in tbl
    has_header = bool(rows) and '<w:tblHeader' in rows[0][:rows[0].find('<w:tc>')]
    if not regular:
        # 含合併儲存格之表格：只套無間距與列不跨頁，欄寬不動
        tbl = re.sub(PARA, lambda m: set_pstyle(m.group(0), f.nosp), tbl, flags=re.S)
        return tbl.replace('<w:trPr>', '<w:trPr><w:cantSplit/>') if '<w:cantSplit/>' not in tbl else tbl
    if fracs and len(fracs) == ncol:
        widths = [round(f.text_w * x) for x in fracs]
        widths[-1] = f.text_w - sum(widths[:-1])
        centre = [False] * ncol
    else:
        kv = False
        widths, centre = auto_widths(cells, ncol, f.text_w, has_header)

    style = re.search(r'<w:tblStyle [^>]*/>', tbl)
    look = re.search(r'<w:tblLook [^>]*/>', tbl)
    out = ('<w:tbl><w:tblPr>%s<w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblLayout w:type="fixed"/>%s%s</w:tblPr>'
           '<w:tblGrid>%s</w:tblGrid>') % (
        style.group(0) if style else '', sum(widths),
        ('<w:tblCellMar><w:top w:w="%d" w:type="dxa"/><w:bottom w:w="%d" w:type="dxa"/></w:tblCellMar>' % (pad, pad)) if pad is not None else '',
        look.group(0) if look else '', ''.join('<w:gridCol w:w="%d"/>' % w for w in widths))
    for ri, (r, cs) in enumerate(zip(rows, cells)):
        head = ri == 0 and has_header
        open_tag = re.match(r'<w:tr(?: [^>]*)?>', r).group(0)
        trpr = re.search(r'<w:trPr>(.*?)</w:trPr>', r[:r.find('<w:tc>')], flags=re.S)
        inner = trpr.group(1) if trpr else ''
        cnf = re.match(r'\s*<w:cnfStyle [^>]*/>', inner)
        inner = (cnf.group(0) if cnf else '') + '<w:cantSplit/>' + inner[cnf.end() if cnf else 0:]
        out += open_tag + '<w:trPr>' + inner + '</w:trPr>'
        section = kv and not head and plain(cs[0]).startswith('§') and all(not plain(c) for c in cs[1:])
        for i, c in enumerate(cs[:1] if section else cs):
            body = re.sub(r'<w:tcPr>.*?</w:tcPr>|<w:tcPr/>', '', c[len('<w:tc>'):-len('</w:tc>')], count=1, flags=re.S)
            jc = 'center' if (head or centre[i]) else 'left'
            body = re.sub(PARA, lambda m: cell_par(m.group(0), f, jc, head), body, flags=re.S)
            if section:
                tcp = ('<w:tcW w:w="%d" w:type="dxa"/><w:gridSpan w:val="%d"/><w:shd w:val="clear" w:color="auto" w:fill="D9D9D9"/>'
                       % (sum(widths), ncol))
            else:
                tcp = '<w:tcW w:w="%d" w:type="dxa"/>' % widths[i]
            cell = '<w:tc><w:tcPr>%s<w:vAlign w:val="center"/></w:tcPr>%s</w:tc>' % (tcp, body)
            if section or (kv and i == 0 and not head):
                cell = bold_cell(cell)
            out += cell
        out += '</w:tr>'
    return out + '</w:tbl>'


FRONT_TABLES = (                     # 章標題關鍵字 → 欄寬比例、是否為欄位表、上下邊界
    (('發行授權', 'Document Availability'), [0.30, 0.70], True, 15),
    (('文件資訊', 'Document Information'), [0.22, 0.78], True, None),
    (('修訂紀錄', 'Revision History'), [0.11, 0.17, 0.20, 0.52], False, None),
)


# ------------------------------------------------------------------ 節與封面
def sect_variant(sect, fmt=None, title_pg=False):
    s = re.sub(r'<w:titlePg[^>]*/>|<w:pgNumType [^>]*/>', '', sect)
    if fmt:
        num = '<w:pgNumType w:fmt="%s" w:start="1"/>' % fmt
        for anchor in ('<w:cols', '<w:docGrid', '</w:sectPr>'):
            if anchor in s:
                s = s.replace(anchor, num + anchor, 1)
                break
    if title_pg:
        anchor = '<w:docGrid' if '<w:docGrid' in s else '</w:sectPr>'
        s = s.replace(anchor, '<w:titlePg/>' + anchor, 1)
    return s


def sect_break(f, sect):
    return ('<w:p><w:pPr><w:pStyle w:val="%s"/><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>'
            '<w:rPr><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr>%s</w:pPr></w:p>') % (f.nosp, sect)


def front_pages(f, cover_blk, title_blk, back_blk, strn):
    """由 MD「封面」「書名頁」兩節之內容組出封面與書名頁（AFRL 版式：置中堆疊、底部告示框）。"""
    def kv_tables(blk):
        return [rows_of(x) for x in blk if x.startswith('<w:tbl>')]

    def heading(blk):
        hs = [plain(x) for x in blk if not x.startswith('<w:tbl>') and pstyle(x) == f.h1]
        return hs[0] if hs else ''

    ct, tt = kv_tables(cover_blk), kv_tables(title_blk)
    ckv = dict(r[:2] for r in ct[0][1:] if len(r) >= 2) if ct else {}
    tools = [r for r in ct[1][1:] if len(r) >= 2] if len(ct) > 1 else []
    tp = [r[:2] for r in tt[0][1:] if len(r) >= 2] if tt else []
    tkv = dict(tp)
    num = ckv.get('報告編號', strn)
    sec = ckv.get('安全等級', '')
    lead = [plain(x) for x in cover_blk[1:] if not x.startswith('<w:tbl>') and pstyle(x) != f.h1 and plain(x)]
    series = lead[0].replace(num, '').strip(' 　—-–') if lead else ''
    review = ''
    for x in back_blk:
        t = plain(x) if not x.startswith('<w:tbl>') else ''
        if t.startswith('審查等級'):
            review = t[len('審查等級'):].strip(' ：:　')
    r, p = f.run, f.para
    notice = [r('安全等級：', 22, True), r(sec + '。', 22), r('　狀態：', 22, True), r(ckv.get('狀態', '') + '。', 22)]
    if review:
        notice += [r('　審查等級：', 22, True), r(review, 22)]
    cover = (p(r(num, 24, True), 'left')
             + p(r(heading(cover_blk), 32, True, caps=True), 'center', before=2800, line=360)
             + p(r(series, 28, True), 'center', before=360)
             + p(r(tkv.get('作者', ''), 24), 'center', before=1200)
             + p(r(tkv.get('專案', ''), 24), 'center', before=120)
             + p(r(tkv.get('階段', ''), 24), 'center', before=120)
             + p(r(ckv.get('日期', ''), 24), 'center', before=1200)
             + p(r('%s　%s' % (ckv.get('狀態', ''), ckv.get('版本', '')), 24, True), 'center', before=120)
             + p(notice, 'left', before=2400, line=300, border=BOX))
    if tools:
        cover += p([r('工具版本：', 20, True), r('；'.join('%s %s' % (a, b) for a, b in tools), 20)],
                   'left', before=200, line=280, border=BOX)
    title = (p(r(num, 24, True), 'left')
             + p(r(heading(title_blk) or heading(cover_blk), 32, True, caps=True), 'center', before=2000, line=360)
             + p(r(series, 28, True), 'center', before=360)
             + p('', before=1400))
    if tp:
        title += f.grid_table(tp, [1800, 5400], ['項目', '內容'])
    return cover, title, num, sec


# ------------------------------------------------------------------ 後處理
def postprocess(parts, strn):
    d = re.sub(r'\s+/>', '/>', parts['word/document.xml'].decode('utf-8'))
    styles = parts['word/styles.xml'].decode('utf-8')
    bm = re.search(r'(<w:body>)(.*)(</w:body>)', d, flags=re.S)
    inner = bm.group(2)
    sm = list(re.finditer(r'<w:sectPr(?: [^>]*)?>.*?</w:sectPr>', inner, flags=re.S))[-1]
    sect = sm.group(0)
    f = Fmt(styles, sect)
    blk = [x for x in re.split('(' + BLOCK + ')', inner[:sm.start()], flags=re.S) if x.strip()]

    def is_par(x):
        return x.startswith('<w:p')

    h2 = [(i, plain(x)) for i, x in enumerate(blk) if is_par(x) and pstyle(x) == f.h2]
    find = lambda test: next((i for i, t in h2 if test(t)), None)
    i_cover = find(lambda t: '封面' in t or 'Cover Page' in t)
    i_title = find(lambda t: ('書名頁' in t and '背面' not in t) or ('Title Page' in t and 'Back' not in t))
    i_body = find(lambda t: re.match(r'\s*1\s*[\.．、\s]', t) or '緒論' in t)
    after = lambda i: next((j for j, _ in h2 if j > i), len(blk))

    cover = title = None
    num, sec, start = strn, '', 0
    if i_cover is not None and i_title is not None and i_cover < i_title:
        start = after(i_title)
        nxt = after(start) if start < len(blk) else len(blk)
        cover, title, num, sec = front_pages(f, blk[i_cover:i_title], blk[i_title:start], blk[start:nxt], strn)
    else:
        print('注意：找不到「封面」「書名頁」兩節，封面未重排。', file=sys.stderr)
    if i_body is None:
        print('注意：找不到第 1 章標題，前頁未改用羅馬數字頁碼。', file=sys.stderr)

    out, chapter = [], ''
    for i in range(start, len(blk)):
        x = blk[i]
        if i == i_body:
            out.append(sect_break(f, sect_variant(sect, 'lowerRoman', title_pg=True)))
        if x.startswith('<w:tbl>'):
            if out and is_par(out[-1]) and re.match(CAPTION, plain(out[-1])):
                out[-1] = set_pstyle(out[-1], f.tcap)
            spec = next((s for s in FRONT_TABLES if any(k in chapter for k in s[0])), None)
            out.append(fmt_table(x, f, spec[1], spec[2], spec[3]) if spec else fmt_table(x, f))
            continue
        st = pstyle(x)
        if st == f.h2:
            chapter = plain(x)
        if i > start and blk[i - 1].startswith('<w:tbl>') and st not in f.heads and plain(x):
            x = space_before(x, 180)
        out.append(x)

    body = ''
    if cover is not None:
        body = cover + sect_break(f, sect_variant(sect, None, title_pg=True)) + title
    last = sect_variant(sect, 'decimal') if i_body is not None else sect_variant(sect, None, title_pg=cover is None)
    d = d[:bm.start(2)] + body + ''.join(out) + last + d[bm.end(2):]
    parts['word/document.xml'] = d.encode('utf-8')

    for name in list(parts):
        if re.match(r'word/(header|footer)\d*\.xml$', name):
            x = parts[name].decode('utf-8')
            if not sec:
                x = x.replace('　｜　〔安全等級〕', '')
            x = x.replace('〔報告編號〕', escape(num)).replace('〔安全等級〕', escape(sec)).replace('{STRN}', escape(num))
            parts[name] = x.encode('utf-8')
            minidom.parseString(parts[name])
    minidom.parseString(parts['word/document.xml'])

    # 範本帶來但本文件未引用之圖檔不留在輸出內
    # （pandoc 會保留範本之圖片關聯，故連同關聯與內容型別一併清除）
    used = set(re.findall(r'r:(?:embed|id|link|pict)="([^"]+)"', d))
    rel_name = 'word/_rels/document.xml.rels'
    rels = parts[rel_name].decode('utf-8')
    ct = parts['[Content_Types].xml'].decode('utf-8')
    for m in re.findall(r'<Relationship [^>]*/>', rels):
        rid = re.search(r'Id="([^"]+)"', m).group(1)
        target = re.search(r'Target="([^"]+)"', m).group(1)
        if '/image"' in m and rid not in used and target.startswith('media/'):
            rels = rels.replace(m, '')
            parts.pop('word/' + target, None)
            ct = re.sub(r'<Override PartName="/word/%s"[^>]*/>' % re.escape(target), '', ct)
    parts[rel_name] = rels.encode('utf-8')
    parts['[Content_Types].xml'] = ct.encode('utf-8')
    return num


def main():
    ap = argparse.ArgumentParser(description='PXA 報告 MD → docx（版面取自 PXA-SP-template.dotx）')
    ap.add_argument('input')
    ap.add_argument('-o', '--output')
    ap.add_argument('--template', '--refdoc', dest='template', default=TEMPLATE)
    ap.add_argument('--no-xref', action='store_true', help='不做交互參照（保留作者年份引用與純文字題注）')
    a = ap.parse_args()
    out = os.path.abspath(a.output or os.path.splitext(a.input)[0] + '.docx')
    src = os.path.abspath(a.input)
    xref = not a.no_xref and not out.lower().endswith('.dotx')

    text = open(src, encoding='utf-8').read()
    pre, strn = preprocess(text)
    report = []
    if xref:
        pre, info, report = docx_xref.md_pass(pre)
    tmp = tempfile.mkdtemp(prefix='md2docx_')
    try:
        ref = os.path.join(tmp, 'template-copy.docx')          # 步驟 0：先複製範本
        write_pkg(ref, read_pkg(a.template))
        premd = os.path.join(tmp, 'pre.md')
        open(premd, 'w', encoding='utf-8').write(pre)
        raw = os.path.join(tmp, 'raw.docx')
        subprocess.run(['pandoc', premd, '-f', 'markdown', '-t', 'docx', '--reference-doc', ref,
                        '--resource-path', os.path.dirname(src), '-o', raw], check=True)
        parts = read_pkg(raw)
        if xref:
            report += docx_xref.docx_pass(parts, info)
        num = postprocess(parts, strn)
        write_pkg(out, parts, as_template=out.lower().endswith('.dotx'))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('OK %s  (報告編號: %s)' % (out, num or 'n/a'))
    if xref:
        print('交互參照：參考文獻 %d 筆、表／圖題注 %d 個；開啟後在 Word 按 Ctrl+A、F9 更新欄位' % (info['refs'], len(info['caps'])))
    for r in report:
        print('注意：' + r)


if __name__ == '__main__':
    main()
