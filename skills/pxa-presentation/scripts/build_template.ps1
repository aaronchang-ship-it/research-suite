<#
.SYNOPSIS
    重建 pxa-presentation 的簡報範本（.potx）與示範簡報（.pptx）。
.DESCRIPTION
    以 PowerPoint 建立母片、佈景主題（配色、字型）與十種版面，另存為範本；
    再用各版面做一份示範簡報。需要本機安裝 PowerPoint；檔案須以 UTF-8（含 BOM）儲存。
    不給 -LogoColor 與 -LogoWhite 時產出不含標誌的中性範本。
.EXAMPLE
    .\build_template.ps1 -OutDir C:\work\out
    .\build_template.ps1 -OutDir C:\work\out -LogoColor C:\brand\logo_color.png -LogoWhite C:\brand\logo_white.png
#>
param(
    [Parameter(Mandatory)][string]$OutDir,   # 產出資料夾（絕對路徑）
    [string]$LogoColor,                       # 全彩標誌，放白底頁右上
    [string]$LogoWhite,                       # 反白標誌，放藍底的封面與章節頁
    [string]$Plot                             # 示範簡報用的圖檔；不給則圖的佔位框留空
)
$ErrorActionPreference = 'Stop'
$Neutral = -not ($LogoColor -and $LogoWhite)
New-Item -ItemType Directory -Force $OutDir | Out-Null

function Set-ThemeHantFont([string]$Path) {
    # 繁中版 PowerPoint 的佈景主題另有 Hant 專用字型，會蓋過東亞字型設定；這裡一併改掉
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [IO.Compression.ZipFile]::Open($Path, 'Update')
    try {
        foreach ($e in @($zip.Entries | Where-Object { $_.FullName -match '^ppt/theme/theme\d+\.xml$' })) {
            $rd = New-Object IO.StreamReader($e.Open(), [Text.Encoding]::UTF8); $x = $rd.ReadToEnd(); $rd.Close()
            $x = $x -replace 'script="Hant" typeface="[^"]*"', 'script="Hant" typeface="Noto Sans TC"'
            $st = $e.Open(); $st.SetLength(0)
            $wr = New-Object IO.StreamWriter($st, (New-Object Text.UTF8Encoding $false)); $wr.Write($x); $wr.Close()
        }
    } finally { $zip.Dispose() }
}

function C([string]$hex) {
    $r = [Convert]::ToInt32($hex.Substring(0,2),16); $g = [Convert]::ToInt32($hex.Substring(2,2),16); $b = [Convert]::ToInt32($hex.Substring(4,2),16)
    return $r + 256*$g + 65536*$b
}
# msoThemeColorIndex
$T1 = 13; $BG1 = 14; $T2 = 15; $BG2 = 16; $A1 = 5; $A2 = 6; $A3 = 7; $A4 = 8; $A5 = 9

$ppt  = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Add(0)
$pres.PageSetup.SlideWidth = 960; $pres.PageSetup.SlideHeight = 540
$m = $pres.SlideMaster
$m.Name = 'PXA Presentation'

# ---- theme ----
$cs = $m.Theme.ThemeColorScheme
$cols = @('1B2733','FFFFFF','0957C3','EEF3F6','0957C3','307FE2','F2A541','5F6B76','C9D3DA','333333','0957C3','5F6B76')
for ($i = 1; $i -le 12; $i++) { $cs.Colors($i).RGB = (C $cols[$i-1]) }
$fs = $m.Theme.ThemeFontScheme
foreach ($k in 1,3) { $fs.MajorFont.Item($k).Name = 'Noto Sans TC'; $fs.MinorFont.Item($k).Name = 'Noto Sans TC' }

# ---- master placeholders ----
foreach ($s in @($m.Shapes)) {
    switch ($s.PlaceholderFormat.Type) {
        1  { $s.Left = 40; $s.Top = 20; $s.Width = $(if ($Neutral) { 880 } else { 715 }); $s.Height = 60
             $s.TextFrame.VerticalAnchor = 3; $s.TextFrame.WordWrap = -1
             $s.TextFrame.MarginLeft = 0; $s.TextFrame.MarginRight = 0; $s.TextFrame.MarginTop = 0; $s.TextFrame.MarginBottom = 0
             $f = $s.TextFrame.TextRange.Font; $f.Size = 28; $f.Bold = -1; $f.Color.ObjectThemeColor = $T2
             $s.TextFrame.TextRange.ParagraphFormat.Alignment = 1
             $s.TextFrame2.AutoSize = 2
             $s.TextFrame.TextRange.Text = '按一下以編輯標題：主題＋結論句' }
        2  { $s.Left = 40; $s.Top = 96; $s.Width = 880; $s.Height = 370
             $s.TextFrame.MarginLeft = 0; $s.TextFrame.MarginRight = 0; $s.TextFrame.MarginTop = 0; $s.TextFrame.MarginBottom = 0
             $sz = 18,16,14,14,14
             for ($i = 1; $i -le 5; $i++) {
                 $p = $s.TextFrame.TextRange.Paragraphs($i)
                 $p.Font.Size = $sz[$i-1]; $p.Font.Color.ObjectThemeColor = $T1
                 $p.ParagraphFormat.SpaceBefore = 6; $p.ParagraphFormat.SpaceWithin = 1.1
                 $p.ParagraphFormat.Bullet.Font.Color.ObjectThemeColor = $T2
                 $q = $s.TextFrame2.TextRange.Paragraphs($i).ParagraphFormat; $q.LeftIndent = 18*$i; $q.FirstLineIndent = -18
             } }
        16 { $s.Delete() }
        15 { $s.Left = 40; $s.Top = 510; $s.Width = 500; $s.Height = 16
             $s.TextFrame.MarginLeft = 0; $s.TextFrame.TextRange.ParagraphFormat.Alignment = 1
             $s.TextFrame.TextRange.Font.Size = 10; $s.TextFrame.TextRange.Font.Color.ObjectThemeColor = $A4 }
        13 { $s.Left = 860; $s.Top = 510; $s.Width = 60; $s.Height = 16
             $s.TextFrame.MarginRight = 0; $s.TextFrame.TextRange.ParagraphFormat.Alignment = 3
             $s.TextFrame.TextRange.Font.Size = 10; $s.TextFrame.TextRange.Font.Color.ObjectThemeColor = $A4 }
    }
}
if (-not $Neutral) { $lg = $m.Shapes.AddPicture($logoColor, 0, -1, 770, 26, 150, 32); $lg.Name = 'Logo' }

# ---- helpers ----
function Flat($s) { $s.TextFrame.MarginLeft = 0; $s.TextFrame.MarginRight = 0; $s.TextFrame.MarginTop = 0; $s.TextFrame.MarginBottom = 0 }
function Ind($s, [int]$i, [single]$left, [single]$first, [int]$bullet) {
    $q = $s.TextFrame2.TextRange.Paragraphs($i).ParagraphFormat
    $q.Bullet.Visible = $bullet; $q.LeftIndent = $left; $q.FirstLineIndent = $first
}
function NoBullet($s, [int]$n) { for ($i = 1; $i -le $n; $i++) { Ind $s $i 0 0 0 } }
function Ph($lay, [int]$type, $l, $t, $w, $h, [string]$prompt, [string]$name) {
    $s = $lay.Shapes.AddPlaceholder($type, $l, $t, $w, $h); $s.Name = $name
    try { $s.LockAspectRatio = 0 } catch { }
    $s.Left = $l; $s.Top = $t; $s.Width = $w; $s.Height = $h
    if ($prompt) { $s.TextFrame.TextRange.Text = $prompt }
    return $s
}
function TextPh($lay, $l, $t, $w, $h, [string]$prompt, [string]$name, [single]$size, [int]$bold, [int]$theme) {
    $s = Ph $lay 2 $l $t $w $h $prompt $name
    Flat $s; NoBullet $s 1
    $f = $s.TextFrame.TextRange.Font; $f.Size = $size; $f.Bold = $bold; $f.Color.ObjectThemeColor = $theme
    $s.TextFrame.TextRange.ParagraphFormat.SpaceBefore = 0
    return $s
}
function Source($lay) {
    $s = TextPh $lay 40 478 880 20 '來源：〔報告圖表編號，或 output\ 的檔名〕' 'Source' 10 0 $A4
    $s.TextFrame.VerticalAnchor = 3
}
function Card($s, [int]$theme) {
    try { $s.AutoShapeType = 5; $s.Adjustments.Item(1) = 0.06 } catch { }
    $s.Fill.Visible = -1; $s.Fill.Solid(); $s.Fill.ForeColor.ObjectThemeColor = $theme; $s.Line.Visible = 0
    $s.TextFrame.MarginLeft = 16; $s.TextFrame.MarginRight = 16; $s.TextFrame.MarginTop = 12; $s.TextFrame.MarginBottom = 12
}
function Stat($lay, $l, $t, $w, $h, [string]$name) {
    $s = Ph $lay 2 $l $t $w $h "數值與單位`r說明（按 Tab 降一階）`r備註（再按一次 Tab）" $name
    Card $s $BG2; $s.TextFrame.VerticalAnchor = 3
    $tr = $s.TextFrame.TextRange
    $tr.Paragraphs(2).IndentLevel = 2; $tr.Paragraphs(3).IndentLevel = 3; NoBullet $s 3
    $p = $tr.Paragraphs(1); $p.Font.Size = 30; $p.Font.Bold = -1; $p.Font.Color.ObjectThemeColor = $T2; $p.ParagraphFormat.SpaceBefore = 0
    $p = $tr.Paragraphs(2); $p.Font.Size = 14; $p.Font.Bold = -1; $p.Font.Color.ObjectThemeColor = $T1; $p.ParagraphFormat.SpaceBefore = 2
    $p = $tr.Paragraphs(3); $p.Font.Size = 12; $p.Font.Bold = 0;  $p.Font.Color.ObjectThemeColor = $A4; $p.ParagraphFormat.SpaceBefore = 2
    return $s
}
function NewLayout([string]$name, [bool]$dark) {
    $lay = $m.CustomLayouts.Add($m.CustomLayouts.Count + 1); $lay.Name = $name
    if ($dark) {
        $lay.FollowMasterBackground = 0; $lay.Background.Fill.Solid(); $lay.Background.Fill.ForeColor.ObjectThemeColor = $T2
        $lay.DisplayMasterShapes = 0
        foreach ($s in @($lay.Shapes)) { if ($s.Type -eq 14 -and $s.PlaceholderFormat.Type -ne 1) { $s.Delete() } }
    } else {
        foreach ($s in @($lay.Shapes)) { if ($s.Type -eq 14 -and $s.PlaceholderFormat.Type -eq 16) { $s.Delete() } }
    }
    return $lay
}
function TitleOf($lay) { foreach ($s in $lay.Shapes) { if ($s.Type -eq 14 -and $s.PlaceholderFormat.Type -eq 1) { return $s } } }

$old = @($m.CustomLayouts)

# 1 封面
$lay = NewLayout '封面' $true
if (-not $Neutral) { $null = $lay.Shapes.AddPicture($logoWhite, 0, -1, 60, 56, 250, 53) }
$t = TitleOf $lay; $t.Left = 60; $t.Top = 170; $t.Width = 840; $t.Height = 100; $t.TextFrame.VerticalAnchor = 4
$t.TextFrame.TextRange.Font.Size = 48; $t.TextFrame.TextRange.Font.Color.ObjectThemeColor = $BG1; $t.TextFrame.TextRange.Text = '簡報標題'
$null = TextPh $lay 60 282 840 40 '副標題：簡報種類｜階段' 'Subtitle' 24 0 $BG1
$null = TextPh $lay 60 384 500 56 "單位`r報告人" 'Presenter' 16 -1 $BG1
$null = TextPh $lay 60 474 600 22 '報告編號 〔文件編號〕　〔版次〕　〔日期〕' 'DocId' 12 0 $BG1

# 2 章節頁
$lay = NewLayout '章節頁' $true
$null = TextPh $lay 60 130 400 96 '00' 'ChapterNo' 80 -1 $BG1
$t = TitleOf $lay; $t.Left = 60; $t.Top = 236; $t.Width = 840; $t.Height = 64; $t.TextFrame.VerticalAnchor = 3
$t.TextFrame.TextRange.Font.Size = 40; $t.TextFrame.TextRange.Font.Color.ObjectThemeColor = $BG1; $t.TextFrame.TextRange.Text = '章節標題'
$null = TextPh $lay 60 312 700 90 '本章要回答的問題，一至兩句' 'ChapterLead' 18 0 $BG1
if (-not $Neutral) { $null = $lay.Shapes.AddPicture($logoWhite, 0, -1, 770, 482, 150, 32) }

# 3 標題及內文
$lay = NewLayout '標題及內文' $false
$s = Ph $lay 2 40 96 880 370 $null 'Body'; Source $lay

# 4 圖與說明
$lay = NewLayout '圖與說明' $false
$null = Ph $lay 18 40 96 540 370 '按一下圖示插入圖片' 'Figure'
$s = Ph $lay 2 604 96 316 370 $null 'Body'; $s.TextFrame.TextRange.Paragraphs(1).Font.Size = 16
Source $lay

# 5 圖與數字卡
$lay = NewLayout '圖與數字卡' $false
$null = Ph $lay 18 40 96 540 370 '按一下圖示插入圖片' 'Figure'
$null = Stat $lay 604 96 316 106 'Stat1'; $null = Stat $lay 604 214 316 106 'Stat2'
$s = TextPh $lay 604 334 316 132 '對圖與數字的說明，兩至三句' 'Note' 14 0 $T1
$s.TextFrame.TextRange.ParagraphFormat.SpaceWithin = 1.15
Source $lay

# 6 表格
$lay = NewLayout '表格' $false
$null = Ph $lay 12 40 96 880 310 '按一下圖示插入表格' 'Table'
$null = TextPh $lay 40 418 880 48 '表格的判讀重點或備註' 'Note' 14 0 $T1
Source $lay

# 7 兩欄對照
$lay = NewLayout '兩欄對照' $false
foreach ($x in 40, 490) {
    $s = Ph $lay 2 $x 96 430 370 "欄標題`r內容（按 Tab 降一階）" ("Column" + $x)
    Card $s $BG2
    $s.TextFrame.TextRange.Paragraphs(2).IndentLevel = 2
    Ind $s 1 0 0 0; Ind $s 2 18 -18 -1
    $p = $s.TextFrame.TextRange.Paragraphs(1); $p.Font.Size = 20; $p.Font.Bold = -1; $p.Font.Color.ObjectThemeColor = $T2
    $p = $s.TextFrame.TextRange.Paragraphs(2); $p.Font.Size = 16; $p.Font.Bold = 0; $p.Font.Color.ObjectThemeColor = $T1
}
Source $lay

# 8 結論頁
$lay = NewLayout '結論頁' $false
$null = Stat $lay 40 96 280 120 'Stat1'; $null = Stat $lay 340 96 280 120 'Stat2'; $null = Stat $lay 640 96 280 120 'Stat3'
$s = Ph $lay 2 40 236 880 230 "論述主線`r結論一（按 Tab 降一階）" 'Thesis'
Card $s $T2; $s.TextFrame.MarginLeft = 24; $s.TextFrame.MarginTop = 20; $s.TextFrame.VerticalAnchor = 1
$s.TextFrame.TextRange.Paragraphs(2).IndentLevel = 2
Ind $s 1 0 0 0; Ind $s 2 26 -26 -1
$p = $s.TextFrame.TextRange.Paragraphs(1); $p.Font.Size = 14; $p.Font.Bold = -1; $p.Font.Color.ObjectThemeColor = $A3
$p = $s.TextFrame.TextRange.Paragraphs(2); $p.Font.Size = 18; $p.Font.Bold = 0; $p.Font.Color.ObjectThemeColor = $BG1
$p.ParagraphFormat.Bullet.Type = 2; $p.ParagraphFormat.SpaceBefore = 8; $p.ParagraphFormat.Bullet.Font.Color.ObjectThemeColor = $BG1
Source $lay

# 9 只有標題
$lay = NewLayout '只有標題' $false; Source $lay
# 10 空白
$lay = NewLayout '空白' $false; (TitleOf $lay).Delete()

foreach ($o in $old) { $o.Delete() }

# footer defaults
foreach ($h in @($m) + @($m.CustomLayouts)) {
    try { $hf = $h.HeadersFooters; $hf.Footer.Visible = -1; $hf.Footer.Text = '〔文件編號〕　〔版次〕'; $hf.SlideNumber.Visible = -1 } catch { }
}

$pres.SaveAs("$OutDir\pxa_presentation_template.potx", 26)
"layouts: " + (@($m.CustomLayouts) | ForEach-Object { $_.Name }) -join ', '

# ================= demo deck =================
function L([string]$n) { foreach ($x in $m.CustomLayouts) { if ($x.Name -eq $n) { return $x } } }
function Fill($sl, [string]$name, [string]$text) { foreach ($s in $sl.Shapes) { if ($s.Name -like "$name*") { $s.TextFrame.TextRange.Text = $text; return $s } }; "  !! no shape $name on slide " + $sl.SlideIndex }
function Lv($s, [int[]]$levels) { for ($i = 0; $i -lt $levels.Count; $i++) { $s.TextFrame.TextRange.Paragraphs($i+1).IndentLevel = $levels[$i] } }
function Own($h) { $o = @(); foreach ($s in $h.Shapes) { if ($s.Type -eq 14 -and (1,13,15,16) -notcontains $s.PlaceholderFormat.Type) { $o += $s } }; return ,$o }
function Add([string]$n) {
    $lay = L $n; $sl = $pres.Slides.AddSlide($pres.Slides.Count + 1, $lay)
    $a = Own $lay; $b = Own $sl
    for ($i = 0; $i -lt $b.Count; $i++) { $b[$i].Name = $a[$i].Name }
    return $sl
}
function Names($sl) { "s" + $sl.SlideIndex + ": " + ((@($sl.Shapes) | ForEach-Object { $_.Name }) -join ' | ') }

$sl = Add '封面'
$sl.Shapes.Title.TextFrame.TextRange.Text = '推進分系統模型驗證結果'
$null = Fill $sl 'Subtitle' '技術審查｜檢核階段'; $null = Fill $sl 'Presenter' "〔單位〕`r〔報告人〕"; $null = Fill $sl 'DocId' '報告編號 XXX-TR-2026-001　v1.0　2026-11-23'

$sl = Add '結論頁'
$sl.Shapes.Title.TextFrame.TextRange.Text = '結論：五項驗證指標全部符合需求'
$i = 0; foreach ($d in @(@('2.1 %','最大推力誤差','需求 ≤ 5 %'), @('3.4 %','最大扭矩誤差','需求 ≤ 5 %'), @('0.7 %','穩態轉速誤差','需求 ≤ 2 %'))) { $i++; $s = Fill $sl "Stat$i" ($d -join "`r"); Lv $s 1,2,3 }
$s = Fill $sl 'Thesis' "論述主線`r推力模型與台架量測的誤差在需求範圍內`r五項驗證指標全部符合需求，最小餘裕 1.3 %`r是否以本模型進入下一階段，請審查會議裁定"; Lv $s 1,2,2,2
$null = Fill $sl 'Source' '來源：報告結論 C-3、C-4（數字為版型示意）'

$sl = Add '章節頁'
$sl.Shapes.Title.TextFrame.TextRange.Text = '驗證方法'
$null = Fill $sl 'ChapterNo' '02'; $null = Fill $sl 'ChapterLead' '以三種證據逐級驗證模型：自洽檢查、對規格書、對台架量測。'

$sl = Add '標題及內文'
$sl.Shapes.Title.TextFrame.TextRange.Text = '驗證方法：先分開看各次系統，再看整機'
$s = Fill $sl 'Body' "第一階段：各次系統以相同輸入做開迴路回放`r差值互不影響，也不經積分累積`r第二階段：整機模型自行積分，與參考軌跡逐點相減`r判定準則在比對前先定，不依結果調整"; Lv $s 1,2,1,2
$null = Fill $sl 'Source' '來源：報告第 2 章（內容為版型示意）'

$sl = Add '圖與數字卡'
$sl.Shapes.Title.TextFrame.TextRange.Text = '推力：模型與台架量測的誤差在需求範圍內'
foreach ($s in @($sl.Shapes)) { if ($Plot -and $s.Name -like 'Figure*') { $null = $sl.Shapes.AddPicture($plot, 0, -1, $s.Left, $s.Top, $s.Width, $s.Height) } }
$s = Fill $sl 'Stat1' "2.1 %`r最大推力誤差`r需求 ≤ 5 %"; Lv $s 1,2,3
$s = Fill $sl 'Stat2' "6 / 6`r量測點在需求內`r全轉速範圍"; Lv $s 1,2,3
$null = Fill $sl 'Note' '最大誤差出現在低轉速段。驗證資料與取參數的資料不同批。'
$null = Fill $sl 'Source' '來源：報告圖 4-2、表 4-1｜output\<單元>\thrust_validation.png（數字為版型示意）'

$sl = Add '圖與說明'
$sl.Shapes.Title.TextFrame.TextRange.Text = '轉速響應：上升時間與量測相符'
foreach ($s in @($sl.Shapes)) { if ($Plot -and $s.Name -like 'Figure*') { $null = $sl.Shapes.AddPicture($plot, 0, -1, $s.Left, $s.Top, $s.Width, $s.Height) } }
$s = Fill $sl 'Body' "步階指令下，模型與量測的上升時間差 6.2 %`r需求為 10 % 以內`r超越量兩者都小於 2 %"; Lv $s 1,2,1
$null = Fill $sl 'Source' '來源：報告圖 4-5（數字為版型示意）'

$sl = Add '表格'
$sl.Shapes.Title.TextFrame.TextRange.Text = '驗證指標：五項全部符合需求'
$rows = @(@('指標','需求','結果','餘裕','判定'), @('最大推力誤差','≤ 5 %','2.1 %','2.9 %','符合'), @('最大扭矩誤差','≤ 5 %','3.4 %','1.6 %','符合'), @('電流誤差','≤ 8 %','4.0 %','4.0 %','符合'), @('上升時間誤差','≤ 10 %','6.2 %','3.8 %','符合'), @('穩態轉速誤差','≤ 2 %','0.7 %','1.3 %','符合'))
$before = $sl.Shapes.Count
$ts = $sl.Shapes.AddTable(6, 5, 40, 96, 880, 280)
"  table: shapes before=$before after=" + $sl.Shapes.Count + " name=" + $ts.Name
for ($r = 1; $r -le 6; $r++) { for ($c = 1; $c -le 5; $c++) {
    $cell = $ts.Table.Cell($r, $c).Shape.TextFrame; $cell.TextRange.Text = $rows[$r-1][$c-1]; $cell.TextRange.Font.Size = 16; $cell.VerticalAnchor = 3
    if ($c -ge 2 -and $c -le 4) { $cell.TextRange.ParagraphFormat.Alignment = 3 }
} }
$null = Fill $sl 'Note' '最小餘裕出現在穩態轉速誤差（1.3 %）。'
$null = Fill $sl 'Source' '來源：報告表 4-3（數字為版型示意）'

$sl = Add '兩欄對照'
$sl.Shapes.Title.TextFrame.TextRange.Text = '已知差異：分為建模與邏輯兩類'
$s = Fill $sl 'Column40' "建模`r雙方採用不同的定義或公式`r差異量級小，可逐項說明來源"; Lv $s 1,2,2
$s = Fill $sl 'Column490' "邏輯`r狀態切換的時間點相差一至數個取樣點`r影響集中在切換瞬間"; Lv $s 1,2,2
$null = Fill $sl 'Source' '來源：報告第 5 章（內容為版型示意）'

$sl = Add '只有標題'
$sl.Shapes.Title.TextFrame.TextRange.Text = '只有標題：流程圖與卡片格自行排在這一頁'
$null = Fill $sl 'Source' '來源：〔報告圖表編號〕'

$pres.SaveCopyAs("$OutDir\pxa_presentation_demo.pptx")
$pres.Saved = -1
$pres.Close()
Set-ThemeHantFont "$OutDir\pxa_presentation_template.potx"
Set-ThemeHantFont "$OutDir\pxa_presentation_demo.pptx"
'done'
