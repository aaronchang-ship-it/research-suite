---
name: pxa-latexer
description: 將 pxa-scribe 產出且定稿的 SP 報告 Report.md 確定性轉換為高品質 LaTeX（.tex，XeLaTeX／繁中排版），供團隊紙本歸檔與審核。凡使用者提到轉 LaTeX、產 .tex、latexer、紙本歸檔版、報告轉 LaTeX 排版、Report.md 轉 tex——即使沒有明說 skill 名稱——都應使用本 skill。範圍到 .tex 定稿為止：編譯（xelatex）由使用者在自己的 TeX 環境執行，本 skill 不編譯、不產 PDF；報告內容變更屬 pxa-scribe，格式規則屬 pxa-standards。
argument-hint: "[選填：Report.md 路徑，如 documents/report/PXA-STRUCT-SP-2026-002.md]"
---

# latexer — SP 報告 Report.md → LaTeX 紙本歸檔版

定位：scribe 的**下游**。輸入＝scribe 定稿的 `Report.md`；輸出＝可直接以 XeLaTeX
編譯的 `.tex`。轉換是**確定性腳本**，不是模型改寫——內容一字不動，只換排版載體，
確保 docx 版與 LaTeX 版內容一致（同一 SSoT 產物、兩種交付形式）。

## 前置條件

- 輸入必須是 **scribe 已定稿**的 Report.md（過了 check_sp gate）。未定稿的草稿先回 scribe。
- 執行環境需 `pandoc`（與 scribe 的 md2docx 同一依賴）。

## 執行

```
python3 <skill根>/scripts/md2tex.py documents/report/{STRN}.md
```

> **腳本執行慣例**：`md2tex.py` 與模板 `templates/pxa-sp-template.tex` 住在本 skill
> 自身目錄（載入時系統告知的 base directory，`<skill根>`），一律從該處執行與取用，
> **禁止複製進使用者專案**。輸出 `.tex` 與 Report.md 同目錄。

腳本自動處理（方言與 md2docx 一致）：頭部 metadata 剝除（自「## 封面」起始）、
STRN 注入頁首、page-break div → `\newpage`、callout → 樣式化引用區塊、
附錄 E 巢狀表提升、`$$…\tag{X}…$$` 原樣保留（amsmath 原生支援，內文「式 (X)」引用不斷鏈）。

模板要點（`templates/pxa-sp-template.tex`）：XeLaTeX＋xeCJK，字型 fallback 鏈
Noto Sans TC → Noto Sans CJK TC → Microsoft JhengHei → Noto Sans CJK HK；A4、
頁首 STRN、頁尾頁碼；SP 標題自帶編號故關閉 LaTeX 自動編號；表格 booktabs/longtable。

## 交付與停止

1. 產出 `.tex` 後，快速自檢：檔案含 `\documentclass` 與 `\end{document}`（腳本已驗）、
   式號與內文「式 (n)」引用抽查 2–3 處一致。
2. 告知使用者編譯方式：**`xelatex {STRN}.tex` 跑兩次**（定頁碼）。需要 TeX Live／MiKTeX
   （含 xeCJK）；亦可丟 Overleaf（compiler 選 XeLaTeX）。
3. **到 .tex 定稿為止即停止**——本 skill 不編譯、不產 PDF。編譯錯誤若源於模板由本 skill
   修模板重轉；若源於內容（scribe 的 MD），回報 scribe 修正，不在 .tex 上手改內容。

## 紅線

1. **內容零改寫**：轉換前後正文內容必須一致；發現 MD 有誤回 scribe，禁止順手在 .tex 修。
2. 版面問題改**模板或腳本**後重轉，禁止手工改個別 .tex 產物（與 scribe「禁止手工改 docx」同理）。
