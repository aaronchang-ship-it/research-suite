#!/usr/bin/env python3
"""PXA 報告 docx 交互參照（md2docx.py 呼叫；只用 Python 標準函式庫）

MD 是作者與審查者的工作稿（作者年份、bibkey），docx 是交付稿（編號引用、Word 原生交互參照）。
MD 不改寫法，轉檔時處理，分兩段：

  md_pass(text)   pandoc 之前：在 MD 中辨識引用、參考文獻、附錄 bibkey、表／圖題注與正文提及，
                  換成純英數記號（QX…QX），並決定參考文獻編號（依正文首次引用排序，未引用者接在最後）
  docx_pass(parts, info)
                  pandoc 之後：把記號換成欄位與書籤
                    - 參考文獻：Word 編號清單 [1]、[2]…＋書籤 _Ref91nnnnn
                    - 正文引用、附錄 bibkey 標題：REF _Ref91nnnnn \\r \\h（顯示 [n]）
                    - 表／圖題注：「表 2-」＋SEQ 表 \\* ARABIC \\s 2＋書籤 _Ref92nnnnn
                    - 正文提及表／圖：REF _Ref92nnnnn \\h；他份報告之表（TR-001 表 2-1）不連結

作者比對（依序）：姓氏 → 全名 → 英文字首縮寫 → 機關名首字 → 報告「縮寫」所宣告者 → 中文字序包含
（完全相符者優先）。同作者同年多筆無法判定時保留原文並回報，不亂連。
"""
import re
import unicodedata

TOKEN = re.compile(r'QX([CBAST])(\d+)QX')
LATIN = r"A-Za-zÀ-ɏ\-'’"
NAME_LATIN = r"(?:[A-Z][%s.]*\s){0,4}[A-Z][%s]*(?:\s+et\s+al\.)?" % (LATIN, LATIN)
NAME_CJK = r"[㐀-鿿]{2,16}"
NAME = r'(?:%s|%s)' % (NAME_LATIN, NAME_CJK)
YEAR = r'(?:19|20)\d\d[a-z]?'
NARRATIVE = re.compile(r'(?P<name>%s)\s?[（(](?P<yrs>%s(?:\s*[、,，;；]\s*%s)*)[）)]' % (NAME, YEAR, YEAR))
PAREN = re.compile(r'[（(](?P<in>[^（）()\n]*?(?:19|20)\d\d[^（）()\n]*)[）)]')
ITEM = re.compile(r'^(?P<pre>.*?)(?P<name>%s)\s?(?P<y>%s)(?![\d\-])(?P<post>.*)$' % (NAME, YEAR), re.S)
BRACKET = re.compile(r'\[(?P<name>%s)\s(?P<y>%s)(?P<post>(?:,\s*[^\]\n]*)?)\]' % (NAME_LATIN, YEAR))
PROTECT = re.compile(r'(\$[^$\n]+\$|`[^`\n]+`|\]\([^)\n]*\)|QX[CBAST]\d+QX)')
LABEL = r'(?:(?P<ch>[A-Z]|\d+)-)?(?P<n>\d+)'
FIG_CAP = re.compile(r'^(?P<pre>\s*!\[)(?P<kind>圖|表)\s?' + LABEL + r'(?![\d\-])')
TAB_CAP = re.compile(r'^(?P<pre>\s*(?:\*\*)?)(?P<kind>表|圖)\s?' + LABEL + r'(?![\d\-])')
MENTION = re.compile(r'(?P<kind>表|圖)\s?' + LABEL + r'(?![\d\-])')


def norm(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c)).strip().lower()


def is_cjk(s):
    return bool(re.fullmatch(NAME_CJK, s))


def subseq(a, b):
    it = iter(b)
    return all(c in it for c in a)


# ------------------------------------------------------------------ 參考文獻與縮寫
class Entry:
    def __init__(self, key, text):
        self.key, self.text = key, text.strip()
        m = re.search(r'[（(]((?:19|20)\d\d)[a-z]?[）)]', self.text)
        self.year = m.group(1) if m else None
        authors = self.text[:m.start()] if m else ''
        self.org = authors.strip().rstrip('.').strip()
        parts = [p.strip() for p in re.split(r'[;；]', authors) if p.strip()]
        self.surnames = [norm(p.split(',')[0]) for p in parts if not re.match(r'et\s+al', p)]
        words = self.org.split()
        self.initials = ''.join(w[0] for w in words if w[:1].isupper()) if len(words) > 1 else ''
        self.first = norm(words[0]) if len(words) > 1 else ''
        s = re.match(r'\D*?\d{4}([a-z])(?![a-z])', key)
        self.suffix = s.group(1) if s else None


def parse_abbrev(text):
    """「**縮寫**：FAA 美國聯邦航空總署（Federal Aviation Administration）；…」與縮寫表列 → 縮寫：名稱集合。"""
    out = {}
    blocks = re.findall(r'\*\*縮寫[^*]*\*\*\s*[:：]?\s*(.+)', text)
    blocks += ['%s %s' % r for r in re.findall(r'^\|\s*([A-Z][A-Za-z0-9/\-]{1,})\s*\|\s*([^|\n]+)\|', text, re.M)]
    for b in blocks:
        for item in re.split(r'[；;]', b):
            m = re.match(r'\s*([A-Z][A-Za-z0-9/\-]{1,})\s+(.+)', item)
            if not m:
                continue
            desc = m.group(2).strip().rstrip('。')
            names = {norm(re.sub(r'[（(].*?[）)]', '', desc))}
            names |= {norm(x) for x in re.findall(r'[（(]([^）)]+)[）)]', desc)}
            out.setdefault(m.group(1), set()).update(n for n in names if n)
    return out


class Resolver:
    def __init__(self, entries, abbrev):
        self.entries, self.abbrev = entries, abbrev

    def candidates(self, name, year, loose):
        y, suf = year[:4], (year[4:] or None)
        name = re.sub(r'\s+et\s+al\.$', '', name.strip())
        n = norm(name)
        pool = [e for e in self.entries if e.year == y and (suf is None or e.suffix == suf)]
        if loose:                                                   # 中文機關簡稱：字序包含
            return [e for e in pool if is_cjk(name) and subseq(name, e.org)]
        return [e for e in pool
                if (e.surnames and n == e.surnames[0]) or n == norm(e.org) or (e.initials and name == e.initials)
                or (e.first and n == e.first) or any(x == norm(e.org) for x in self.abbrev.get(name, ()))]

    def resolve(self, name, year):
        """回傳 (entry, 用到的名稱, 未連結原因)；name 可帶前綴文字，取能比對的最長尾段；完全相符優先。"""
        if is_cjk(name):
            tails = [name[i:] for i in range(len(name) - 1)]
        else:
            w = name.split()
            tails = [' '.join(w[i:]) for i in range(len(w))]
            tails = [t for t in tails if not re.match(r'(?:et|al\.)', t)]
        for loose in (False, True):
            for t in tails:
                c = self.candidates(t, year, loose)
                if len(c) == 1:
                    return c[0], t, None
                if len(c) > 1:
                    return None, t, '同作者同年多筆（%s）' % '、'.join(e.key for e in c)
        return None, None, None


# ------------------------------------------------------------------ MD 段
def h2_sections(lines):
    out, fenced = [], False
    for i, l in enumerate(lines):
        if l.strip().startswith('```'):
            fenced = not fenced
        elif not fenced and re.match(r'##\s', l):
            out.append(i)
    return out


def md_pass(text):
    lines = text.split('\n')
    heads = h2_sections(lines)
    bounds = list(zip(heads, heads[1:] + [len(lines)]))
    title = lambda i: lines[i]
    i_ref = next((a for a, _ in bounds if re.search(r'參考文獻|References', title(a))), None)
    i_body = next((a for a, _ in bounds if re.match(r'##\s*1\s*[\.．]', title(a))), heads[0] if heads else 0)
    verbatim = [(a, b) for a, b in bounds if re.search(r'附錄|Appendix', title(a)) and re.search(r'逐字|Verbatim', title(a))]
    report = []

    entries = []
    if i_ref is not None:
        b = next(b for a, b in bounds if a == i_ref)
        for k in range(i_ref + 1, b):
            m = re.match(r'\s*[-*]\s*\*\*\[(.+?)\]\*\*\s*(.*)$', lines[k])
            if m:
                entries.append((k, Entry(m.group(1), m.group(2))))
    res = Resolver([e for _, e in entries], parse_abbrev(text))
    order = []                                                  # 依首次引用排序之 bibkey

    def num(e):
        if e.key not in order:
            order.append(e.key)
        return order.index(e.key) + 1

    # ---- 表／圖題注
    caps, chap, seq = {}, None, {}
    for i, l in enumerate(lines):
        if i in heads:
            m = re.match(r'##\s*(\d+)\s*[\.．]|##\s*(?:附錄|Appendix)\s*([A-Z])', l)
            chap = (m.group(1) or m.group(2)) if m else None
            seq = {}
            continue
        m = FIG_CAP.match(l)
        if not m:
            m = TAB_CAP.match(l)
            nxt = next((x for x in lines[i + 1:i + 4] if x.strip()), '')
            if not (m and nxt.lstrip().startswith('|')):
                m = None
        if not m:
            continue
        kind, ch, n = m.group('kind'), m.group('ch'), int(m.group('n'))
        label = '%s %s%d' % (kind, (ch + '-') if ch else '', n)
        if label in [c['label'] for c in caps.values()]:
            report.append('題注重複：%s（第 %d 行），第二筆不連結' % (label, i + 1))
            continue
        cid = len(caps) + 1
        seq[kind] = seq.get(kind, 0) + 1
        caps[cid] = dict(kind=kind, ch=ch, n=n, label=label)
        if ch and chap and ch != chap:
            report.append('題注所在章與編號不符：%s 位於第 %s 章（Word 更新欄位後會依所在章重新計數）' % (label, chap))
        elif ch and seq[kind] != n:
            report.append('題注編號不連續：%s 為該章第 %d 個%s（Word 更新欄位後會顯示 %s-%d）' % (label, seq[kind], kind, ch, seq[kind]))
        lines[i] = l[:m.start('kind')] + 'QXS%dQX' % cid + l[m.end():]
    by_label = {c['label']: cid for cid, c in caps.items()}

    # ---- 引用與表／圖提及
    def do_cites(seg, where):
        def narrative(m):
            name, yrs = m.group('name'), re.split(r'\s*[、,，;；]\s*', m.group('yrs'))
            hits, used = [], None
            for y in yrs:
                e, t, why = res.resolve(name, y)
                if not e:
                    if why or t or any(x.year == y[:4] for x in res.entries):
                        report.append('引用未連結：%s（%s）%s' % (name.strip(), y, '：' + why if why else ''))
                    return m.group(0)
                hits.append(e)
                used = t
            pre = name[:len(name) - len(used)]
            return pre + used + ' ' + '、'.join('QXC%dQX' % num(e) for e in hits)

        def item(it):
            m = ITEM.match(it)
            if not m:
                return it
            e, t, why = res.resolve(m.group('name'), m.group('y'))
            if not e:
                if why or any(x.year == m.group('y')[:4] for x in res.entries):
                    report.append('引用未連結：%s %s%s' % (m.group('name').strip(), m.group('y'), '：' + why if why else ''))
                return it
            pre = m.group('pre') + m.group('name')[:len(m.group('name')) - len(t)]
            return pre + t + ' QXC%dQX' % num(e) + m.group('post')

        def paren(m):
            parts = re.split(r'([、；;]\s*)', m.group('in'))
            new = ''.join(p if k % 2 else item(p) for k, p in enumerate(parts))
            return m.group(0)[0] + new + m.group(0)[-1]

        def bracket(m):
            e, t, why = res.resolve(m.group('name'), m.group('y'))
            if not e:
                return m.group(0)
            return m.group('name') + ' QXC%dQX' % num(e) + m.group('post')

        seg = NARRATIVE.sub(narrative, seg)
        seg = PAREN.sub(paren, seg)
        seg = BRACKET.sub(bracket, seg)

        def mention(m):
            lab = '%s %s%s' % (m.group('kind'), (m.group('ch') + '-') if m.group('ch') else '', m.group('n'))
            if lab not in by_label or re.search(r'TR-\d{3}\s*$', seg_cur[0][:m.start()]):
                return m.group(0)
            return 'QXT%dQX' % by_label[lab]
        seg_cur = [seg]
        return MENTION.sub(mention, seg)

    skip = set()
    if i_ref is not None:
        skip |= set(range(i_ref, next(b for a, b in bounds if a == i_ref)))
    for a, b in verbatim:
        skip |= set(range(a + 1, b))
    in_math = fenced = False
    for i in range(i_body, len(lines)):
        l = lines[i]
        s = l.strip()
        if s.startswith('```'):
            fenced = not fenced
        if s == '$$':
            in_math = not in_math
        if fenced or in_math or s == '$$' or i in skip:
            continue
        parts = PROTECT.split(l)
        lines[i] = ''.join(p if k % 2 else do_cites(p, i) for k, p in enumerate(parts))

    # ---- 附錄逐字摘錄之 bibkey 標題
    keys = {e.key: e for _, e in entries}
    for a, b in verbatim:
        for i in range(a + 1, b):
            m = re.match(r'(#{3,6}\s*)\[(.+?)\](.*)$', lines[i])
            if m and m.group(2) in keys:
                lines[i] = m.group(1) + 'QXA%dQX' % num(keys[m.group(2)]) + m.group(3)

    # ---- 參考文獻：依編號重排
    uncited = [e.key for _, e in entries if e.key not in order]
    for k in uncited:
        order.append(k)
    if uncited:
        report.append('參考文獻列有但正文未引用（排在最後）：%s' % '、'.join(uncited))
    if entries:
        first, last = entries[0][0], entries[-1][0]
        block = []
        for k in order:
            block += ['QXB%dQX%s' % (order.index(k) + 1, keys[k].text), '']
        lines[first:last + 1] = block[:-1]
    info = dict(refs=len(order), caps=caps, keys=order)
    seen = {}
    for r in report:                                            # 相同訊息只列一次，附次數
        seen[r] = seen.get(r, 0) + 1
    report = [r + ('（%d 處）' % n if n > 1 else '') for r, n in seen.items()]
    return '\n'.join(lines), info, report


# ------------------------------------------------------------------ docx 段
RUN = re.compile(r'<w:r(?: [^>]*)?>(?:(?!</w:r>).)*?</w:r>', re.S)


def field(instr, result, rpr):
    r = lambda inner: '<w:r>%s%s</w:r>' % (rpr, inner)
    return (r('<w:fldChar w:fldCharType="begin"/>') + r('<w:instrText xml:space="preserve"> %s </w:instrText>' % instr)
            + r('<w:fldChar w:fldCharType="separate"/>') + r('<w:t xml:space="preserve">%s</w:t>' % result)
            + r('<w:fldChar w:fldCharType="end"/>'))


def docx_pass(parts, info):
    d = parts['word/document.xml'].decode('utf-8')
    caps = info['caps']
    bm_ref = lambda n: '_Ref%d' % (9100000 + n)
    bm_cap = lambda c: '_Ref%d' % (9200000 + c)

    def cap_prefix(c):
        x = caps[c]
        return '%s %s' % (x['kind'], (x['ch'] + '-') if x['ch'] else '')

    done = set()

    def build(kind, n, rpr):
        if kind == 'S' and n in done:                              # 圖檔缺漏時 pandoc 以說明文字代圖，題注只做一次
            return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, caps[n]['label'])
        done.add((kind, n) if kind != 'S' else n)
        if kind in 'CA':
            return field('REF %s \\r \\h' % bm_ref(n), '[%d]' % n, rpr)
        if kind == 'T':
            return field('REF %s \\h' % bm_cap(n), caps[n]['label'], rpr)
        if kind == 'S':
            x = caps[n]
            instr = 'SEQ %s \\* ARABIC' % x['kind'] + (' \\s 2' if x['ch'] else '')
            return ('<w:bookmarkStart w:id="%d" w:name="%s"/>' % (9200000 + n, bm_cap(n))
                    + '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, cap_prefix(n))
                    + field(instr, str(x['n']), rpr) + '<w:bookmarkEnd w:id="%d"/>' % (9200000 + n))
        return ''                                                   # B：段落層處理

    def split_run(m):
        r = m.group(0)
        if 'QX' not in r:
            return r
        t = re.search(r'<w:t(?: [^>]*)?>([^<]*)</w:t>', r)
        if not t or not TOKEN.search(t.group(1)):
            return r
        rp = re.search(r'<w:rPr>.*?</w:rPr>', r, re.S)
        rpr = rp.group(0) if rp else ''
        out, pos, txt = '', 0, t.group(1)
        for k in TOKEN.finditer(txt):
            if k.start() > pos:
                out += '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, txt[pos:k.start()])
            out += build(k.group(1), int(k.group(2)), rpr)
            pos = k.end()
        if pos < len(txt):
            out += '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, txt[pos:])
        return out

    # 參考文獻段落：編號清單＋書籤
    num_id = add_numbering(parts)

    def ref_par(m):
        p = m.group(0)
        k = re.search(r'QXB(\d+)QX', p)
        if not k:
            return p
        n = int(k.group(1))
        p = p.replace(k.group(0), '', 1)
        numpr = '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="%d"/></w:numPr>' % num_id
        if '<w:pPr>' in p:
            p = re.sub(r'(<w:pPr>(?:<w:pStyle [^>]*/>)?)', r'\g<1>' + numpr, p, count=1)
            p = p.replace('</w:pPr>', '</w:pPr><w:bookmarkStart w:id="%d" w:name="%s"/>' % (9100000 + n, bm_ref(n)), 1)
        else:
            p = re.sub(r'(<w:p(?: [^>]*)?>)', r'\g<1><w:pPr>%s</w:pPr><w:bookmarkStart w:id="%d" w:name="%s"/>'
                       % (numpr, 9100000 + n, bm_ref(n)), p, count=1)
        return p[:-len('</w:p>')] + '<w:bookmarkEnd w:id="%d"/></w:p>' % (9100000 + n)

    d = re.sub(r'<w:p(?: [^>]*)?>(?:(?!</w:p>).)*?</w:p>', ref_par, d, flags=re.S)
    d = RUN.sub(split_run, d)

    # 屬性（圖之替代文字）內殘留之記號 → 純文字
    def plain_tok(m):
        k, n = m.group(1), int(m.group(2))
        return {'C': '[%d]' % n, 'A': '[%d]' % n, 'B': ''}.get(k) or caps[n]['label']
    left = TOKEN.findall(re.sub(r'="[^"]*"', '', d))
    d = TOKEN.sub(plain_tok, d)
    parts['word/document.xml'] = d.encode('utf-8')
    rep = []
    if left:
        rep.append('有 %d 個記號未能轉成欄位（已改為純文字）' % len(left))
    return rep


def add_numbering(parts):
    """新增「[%1]」編號清單定義，回傳 numId。"""
    name = 'word/numbering.xml'
    if name not in parts:
        parts[name] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                       '<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"></w:numbering>').encode('utf-8')
        rels = parts['word/_rels/document.xml.rels'].decode('utf-8')
        rels = rels.replace('</Relationships>', '<Relationship Id="rIdXrefNum" Type="http://schemas.openxmlformats.org/'
                            'officeDocument/2006/relationships/numbering" Target="numbering.xml"/></Relationships>')
        parts['word/_rels/document.xml.rels'] = rels.encode('utf-8')
        ct = parts['[Content_Types].xml'].decode('utf-8')
        ct = ct.replace('</Types>', '<Override PartName="/word/numbering.xml" ContentType="application/vnd.'
                        'openxmlformats-officedocument.wordprocessingml.numbering+xml"/></Types>')
        parts['[Content_Types].xml'] = ct.encode('utf-8')
    n = parts[name].decode('utf-8')
    aid = max([int(x) for x in re.findall(r'w:abstractNumId="(\d+)"', n)] + [0]) + 1
    nid = max([int(x) for x in re.findall(r'<w:num w:numId="(\d+)"', n)] + [0]) + 1
    absn = ('<w:abstractNum w:abstractNumId="%d"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0">'
            '<w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="[%%1]"/><w:lvlJc w:val="left"/>'
            '<w:pPr><w:ind w:left="567" w:hanging="567"/></w:pPr></w:lvl></w:abstractNum>') % aid
    num = '<w:num w:numId="%d"><w:abstractNumId w:val="%d"/></w:num>' % (nid, aid)
    i = n.find('<w:num ')
    n = (n[:i] + absn + n[i:]) if i >= 0 else n.replace('</w:numbering>', absn + '</w:numbering>')
    n = n.replace('</w:numbering>', num + '</w:numbering>')
    parts[name] = n.encode('utf-8')
    return nid
