#!/usr/bin/env python3
"""PXA SP Report.md → LaTeX (.tex) 轉換（latexer 交付管線）

用法:
    python3 md2tex.py <Report.md> [-o out.tex] [--template pxa-sp-template.tex]

與 scribe 的 md2docx.py 同構：前處理同一套 Report.md 方言，後端改 pandoc -t latex。
流程（確定性，同一輸入產出同一 .tex）:
  1. 前處理 MD（方言與 md2docx 一致）:
     - 擷取 STRN（頭部「文件編號」行）→ 傳入模板頁首
     - 剝除 MD 頭部 metadata（自「## 封面」起始）
     - page-break div → \\newpage（其後緊鄰之 `---` 一併移除）
     - callout `> [!NOTE] 標題` → 引用區塊首行 **NOTE｜標題**（模板 quote 環境樣式化）
     - 清單內縮排表格（附錄 E）提升為頂層表格
     - `$$…\\tag{X}…$$` 原樣保留——LaTeX/amsmath 原生支援 \\tag，不需改寫
  2. pandoc -f markdown -t latex --standalone --template <模板>
  3. 驗證輸出含 \\documentclass 與 \\end{document}

輸出 .tex 以 XeLaTeX 編譯（含繁中，模板已設 xeCJK 與字型 fallback）。
本 skill 範圍到 .tex 定稿為止——編譯由使用者在自己的 TeX 環境執行：
    xelatex <out.tex>   （跑兩次以定頁碼）
"""
import argparse, os, re, subprocess, sys, tempfile

CALLOUT = {"NOTE": "NOTE", "IMPORTANT": "IMPORTANT", "TIP": "TIP"}


def preprocess(text: str) -> tuple[str, str]:
    # STRN：取 MD 頭部「文件編號」行
    m = re.search(r"文件編號[:：]\*{0,2}\s*([A-Za-z0-9+\-]+)", text)
    strn = m.group(1) if m else ""

    # 1) 剝除頭部 metadata：自檔首至第一個「## 封面」前
    i = text.find("## 封面")
    if i > 0:
        text = text[i:]

    lines = text.split("\n")
    out = []
    skip_next_hr = False
    for ln in lines:
        s = ln.strip()
        if s.startswith("<div") and "page-break-after" in s:
            out.append("\n```{=latex}\n\\newpage\n```\n")
            skip_next_hr = True
            continue
        if skip_next_hr:
            if s == "":
                continue
            if s == "---":
                skip_next_hr = False
                continue
            skip_next_hr = False
        # 清單項內縮排表格（附錄 E 引用摘錄）→ 提出為頂層表格
        if re.match(r"^ {2,3}\|", ln):
            if out and out[-1].strip() != "" and not out[-1].lstrip().startswith("|"):
                out.append("")
            out.append(ln.lstrip())
            continue
        # callout 首行
        mm = re.match(r">\s*\[!(NOTE|IMPORTANT|TIP)\]\s*(.*)", s)
        if mm:
            tag, rest = mm.group(1), mm.group(2).strip().strip("*").strip()
            label = f"**{CALLOUT[tag]}**" if not rest else f"**{CALLOUT[tag]}｜{rest}**"
            out.append("> " + label)
            continue
        out.append(ln)
    return "\n".join(out), strn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output")
    ap.add_argument("--template", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "templates", "pxa-sp-template.tex"))
    a = ap.parse_args()
    out = a.output or os.path.splitext(a.input)[0] + ".tex"

    text = open(a.input, encoding="utf-8").read()
    pre, strn = preprocess(text)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(pre)
        premd = f.name
    try:
        subprocess.run([
            "pandoc", premd, "-f", "markdown", "-t", "latex",
            "--standalone", "--template", a.template,
            "-V", f"strn={strn}",
            "-o", out,
        ], check=True)
    finally:
        os.unlink(premd)

    tex = open(out, encoding="utf-8").read()
    if "\\documentclass" not in tex or "\\end{document}" not in tex:
        print("！輸出不完整（缺 documentclass / end{document}），請檢查模板", file=sys.stderr)
        sys.exit(1)
    print(f"OK {out}  (STRN: {strn or 'n/a'})")
    print("編譯（使用者本機）：xelatex 跑兩次以定頁碼／交叉引用。")


if __name__ == "__main__":
    main()
