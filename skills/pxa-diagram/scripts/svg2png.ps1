<#
.SYNOPSIS
    把 SVG 轉成 PNG（預設放大 2 倍），用 Microsoft Edge 的無頭模式，不需另外安裝工具。
.DESCRIPTION
    讀 SVG 的 width / height，產生暫存預覽頁，由 Edge 截圖成同名 .png（放在 SVG 旁邊）。
    已存在的同名 PNG 會被覆寫。
.EXAMPLE
    .\svg2png.ps1 -Svg C:\work\fig\block_folder_flow.svg
    .\svg2png.ps1 -Svg C:\work\fig\a.svg, C:\work\fig\b.svg -Scale 3
#>
param(
    [Parameter(Mandatory)][string[]]$Svg,   # 一個或多個 SVG 的絕對路徑
    [int]$Scale = 2                          # 放大倍數
)
$ErrorActionPreference = 'Stop'
$edge = @("${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
          "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw '找不到 Microsoft Edge。' }

foreach ($f in $Svg) {
    $item = Get-Item $f
    [xml]$x = Get-Content $item.FullName -Raw -Encoding UTF8
    $w = [int][double]($x.svg.width  -replace '[^\d.]', '')
    $h = [int][double]($x.svg.height -replace '[^\d.]', '')
    if ($w -le 0 -or $h -le 0) { throw "$($item.Name)：<svg> 要寫 width 與 height。" }

    $png  = [IO.Path]::ChangeExtension($item.FullName, '.png')
    $page = Join-Path $item.DirectoryName ('_svg2png_' + $item.BaseName + '.html')
    $html = "<!doctype html><meta charset='utf-8'><style>html,body{margin:0;background:#fff}img{display:block}</style>" +
            "<img src='$($item.Name)' width='$w' height='$h'>"
    [IO.File]::WriteAllText($page, $html, (New-Object Text.UTF8Encoding $false))
    if (Test-Path $png) { Remove-Item $png }
    $uri = ([Uri]$page).AbsoluteUri
    $edgeArgs = @('--headless=new', '--disable-gpu', '--hide-scrollbars', "--force-device-scale-factor=$Scale",
                  "--window-size=$w,$h", "--screenshot=$png", $uri)
    try {
        # Edge 把進度訊息寫到 stderr；用 Start-Process 執行，避免被當成錯誤
        Start-Process -FilePath $edge -ArgumentList $edgeArgs -Wait -WindowStyle Hidden
        for ($i = 0; $i -lt 50 -and -not (Test-Path $png); $i++) { Start-Sleep -Milliseconds 200 }
    } finally { Remove-Item $page -ErrorAction SilentlyContinue }
    if (-not (Test-Path $png)) { throw "$($item.Name)：轉檔失敗。" }
    '{0} → {1}（{2} × {3} px）' -f $item.Name, (Split-Path $png -Leaf), ($w * $Scale), ($h * $Scale)
}
