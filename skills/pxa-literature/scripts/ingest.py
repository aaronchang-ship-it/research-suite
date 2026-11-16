#!/usr/bin/env python3
"""temp → source/ 入庫（literature skill 快速指令的機械端）

用法:
    ingest.py check --manifest m.json --source <source/> [--vault <vault/sources>]
    ingest.py move  --manifest m.json --source <source/> [--vault <vault/sources>]

分工：**模型負責抽 metadata**（讀 temp 檔首頁得 年份/作者/完整標題，寫入 manifest），
**本腳本負責確定性檢核與搬移**——與 source/ 既有檔名及 vault source notes 去重比對、
產生合規檔名（YYYY 作者 完整標題.ext，Windows 非法字元清洗）、執行搬移。

manifest（JSON list）每筆:
    {"file": "temp/x.pdf", "year": "2019", "author": "Kamal",
     "title": "Schrenk vs CFD UAV Wing Loading", "subdir": "Paper"}
subdir 選填（Paper/Textbooks/Thesis/...，預設 Paper）。

check＝只比對回報（NEW / DUP-FILE / DUP-VAULT / SIMILAR），JSON 輸出供差異回報。
move＝再跑一次比對，僅搬移判定 NEW 者；DUP/SIMILAR 一律不動、留 temp 交使用者裁定。
結束碼: 0 = 正常; 1 = manifest 缺欄位或檔案不存在。
"""
import argparse, difflib, json, os, re, shutil, sys, unicodedata

ILLEGAL = r'[<>:"/\\|?*\x00-\x1f]'


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").lower()
    return re.sub(r"[^a-z0-9一-鿿]+", "", t)


def clean_name(s):
    s = re.sub(ILLEGAL, " ", s)
    return re.sub(r"\s+", " ", s).strip().rstrip(".")


def scan_source(source_dir):
    """source/ 既有檔：{norm(basename 去副檔名): relpath}"""
    out = {}
    for dp, dn, fs in os.walk(source_dir):
        dn[:] = [d for d in dn if not d.startswith(".")]
        for f in fs:
            out[norm(os.path.splitext(f)[0])] = os.path.relpath(os.path.join(dp, f), source_dir)
    return out


def scan_vault(vault_dir):
    """vault sources notes：{norm(title 或檔名): note 名}"""
    out = {}
    if not vault_dir or not os.path.isdir(vault_dir):
        return out
    for f in os.listdir(vault_dir):
        if not f.endswith(".md"):
            continue
        txt = open(os.path.join(vault_dir, f), encoding="utf-8", errors="ignore").read()
        m = re.search(r"^title:\s*(.+)$", txt, re.M)
        if m:
            out[norm(m.group(1).strip().strip('"'))] = f[:-3]
        out[norm(f[:-3])] = f[:-3]
    return out


def classify(entry, src_idx, vault_idx):
    year, author, title = entry["year"], entry["author"], entry["title"]
    newname = clean_name(f"{year} {author} {title}")
    key_full, key_title = norm(newname), norm(title)
    # 完全重複：source/ 或 vault 已有同標題
    for k, hits, tag in ((key_title, src_idx, "DUP-FILE"), (key_title, vault_idx, "DUP-VAULT")):
        for kk, v in hits.items():
            if key_title and key_title in kk or (kk and kk in key_full):
                return tag, v, newname
    # 近似：標題相似度 > 0.82
    best, score = None, 0.0
    for kk, v in {**src_idx, **vault_idx}.items():
        s = difflib.SequenceMatcher(None, key_title, kk).ratio()
        if s > score:
            best, score = v, s
    if score > 0.82:
        return "SIMILAR", f"{best} (相似度 {score:.2f})", newname
    return "NEW", None, newname


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "move"])
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--vault", default=None, help="vault 的 sources/ 目錄")
    a = ap.parse_args()

    entries = json.load(open(a.manifest, encoding="utf-8"))
    for e in entries:
        for k in ("file", "year", "author", "title"):
            if not e.get(k):
                print(f"manifest 缺欄位 {k}: {e}", file=sys.stderr)
                sys.exit(1)
        if not os.path.isfile(e["file"]):
            print(f"檔案不存在: {e['file']}", file=sys.stderr)
            sys.exit(1)

    src_idx = scan_source(a.source)
    vault_idx = scan_vault(a.vault)

    report = []
    for e in entries:
        status, match, newname = classify(e, src_idx, vault_idx)
        ext = os.path.splitext(e["file"])[1]
        subdir = e.get("subdir", "Paper")
        dest = os.path.join(a.source, subdir, newname + ext)
        report.append({"file": e["file"], "status": status, "match": match,
                       "new_name": newname + ext, "dest": dest.replace("\\", "/")})

    if a.cmd == "move":
        for r in report:
            if r["status"] != "NEW":
                r["moved"] = False
                continue
            os.makedirs(os.path.dirname(r["dest"]), exist_ok=True)
            shutil.move(r["file"], r["dest"])
            r["moved"] = True

    json.dump(report, sys.stdout, ensure_ascii=False, indent=1)
    print()
    n = sum(1 for r in report if r["status"] == "NEW")
    print(f"# {len(report)} 筆：NEW {n}／DUP {sum(1 for r in report if r['status'].startswith('DUP'))}"
          f"／SIMILAR {sum(1 for r in report if r['status'] == 'SIMILAR')}"
          + ("（move：僅 NEW 已搬移，其餘留 temp）" if a.cmd == "move" else ""), file=sys.stderr)


if __name__ == "__main__":
    main()
