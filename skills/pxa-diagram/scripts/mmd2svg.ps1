<#
.SYNOPSIS
    把 Mermaid 原始檔（.mmd）轉成 SVG，必要時再轉 PNG；用 Microsoft Edge 無頭模式執行 Mermaid。
.DESCRIPTION
    產生暫存頁，從 jsdelivr CDN 載入 mermaid@11.4.1 與 layout-elk@0.1.7（需要連網；只下載程式庫，
    不上傳任何內容），渲染後取出 SVG，補上 width / height，存成同名 .svg（放在 .mmd 旁邊）。
    加 -Png 時再呼叫同資料夾的 svg2png.ps1。已存在的同名檔會被覆寫。
.EXAMPLE
    .\mmd2svg.ps1 -Mmd C:\work\fig\flow_retry.mmd -Png
#>
param(
    [Parameter(Mandatory)][string[]]$Mmd,   # 一個或多個 .mmd 的絕對路徑
    [switch]$Png,                            # 同時輸出 PNG
    [int]$Scale = 2                          # PNG 放大倍數
)
$ErrorActionPreference = 'Stop'
$edge = @("${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
          "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw '找不到 Microsoft Edge。' }
$cdn = 'https://cdn.jsdelivr.net/npm'

foreach ($f in $Mmd) {
    $item = Get-Item $f
    $src  = [IO.File]::ReadAllText($item.FullName, [Text.Encoding]::UTF8)   # 純字串；Get-Content 會帶 PS 屬性進 JSON
    # 原始碼以 JSON 字串放進頁面，避免引號與換行出錯
    $json = (@{ s = $src } | ConvertTo-Json -Compress) -replace '</', '<\/'
    $page = Join-Path $item.DirectoryName ('_mmd2svg_' + $item.BaseName + '.html')
    $dom  = Join-Path $item.DirectoryName ('_mmd2svg_' + $item.BaseName + '.txt')
    $html = @"
<!doctype html><meta charset="utf-8"><body><script type="module">
import mermaid from "$cdn/mermaid@11.4.1/dist/mermaid.esm.min.mjs";
import elk from "$cdn/@mermaid-js/layout-elk@0.1.7/dist/mermaid-layout-elk.esm.min.mjs";
mermaid.registerLayoutLoaders(elk);
// 排版設定寫在這裡（Mermaid 11.4.1 不採用 .mmd 檔頭的 layout / elk / flowchart 設定）；HTML 嵌入時用同一組
mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', htmlLabels: false, layout: 'elk',
  elk: { mergeEdges: false, nodePlacementStrategy: 'NETWORK_SIMPLEX', cycleBreakingStrategy: 'MODEL_ORDER', considerModelOrder: 'NODES_AND_EDGES' },
  flowchart: { htmlLabels: false, curve: 'linear', padding: 12 },
  sequence: { mirrorActors: false, wrap: true, width: 170 } });
const SRC = $json.s;
try { const r = await mermaid.render('mmdsvg', SRC); document.body.innerHTML = '<div id="ok">' + r.svg + '</div>'; }
catch (e) { document.body.innerHTML = '<pre id="err">' + String(e && e.message || e).replace(/</g, '&lt;') + '</pre>'; }
</script></body>
"@
    [IO.File]::WriteAllText($page, $html, (New-Object Text.UTF8Encoding $false))
    $uri = ([Uri]$page).AbsoluteUri
    try {
        # Edge 把進度訊息寫到 stderr；用 Start-Process 執行，避免被當成錯誤
        Start-Process -FilePath $edge -ArgumentList @('--headless=new', '--disable-gpu', '--virtual-time-budget=20000',
            '--dump-dom', $uri) -Wait -WindowStyle Hidden -RedirectStandardOutput $dom -RedirectStandardError "$dom.err"
        $out = [IO.File]::ReadAllText($dom, [Text.Encoding]::UTF8)
    } finally { Remove-Item $page, $dom, "$dom.err" -ErrorAction SilentlyContinue }

    $err = [regex]::Match($out, '(?s)<pre id="err">(.*?)</pre>')
    if ($err.Success) { throw "$($item.Name)：Mermaid 渲染失敗：$($err.Groups[1].Value)" }
    $svg = [regex]::Match($out, '(?s)<div id="ok">(<svg.*</svg>)</div>').Groups[1].Value
    if (-not $svg) { throw "$($item.Name)：沒有取得 SVG（檢查網路能否連到 cdn.jsdelivr.net）。" }

    # Mermaid 輸出 width="100%"；改成 viewBox 的實際尺寸，svg2png 與文件才有固定大小
    $vb = ([regex]::Match($svg, 'viewBox="([^"]+)"').Groups[1].Value) -split '[ ,]+'
    $w = [math]::Ceiling([double]$vb[2]); $h = [math]::Ceiling([double]$vb[3])
    $head = [regex]::Match($svg, '^<svg[^>]*>').Value
    $newHead = $head -replace '\swidth="[^"]*"', '' -replace '\sheight="[^"]*"', '' -replace '\sstyle="[^"]*"', ''
    $newHead = $newHead -replace '^<svg', "<svg width=`"$w`" height=`"$h`""
    $svg = $newHead + $svg.Substring($head.Length)

    $svgPath = [IO.Path]::ChangeExtension($item.FullName, '.svg')
    [IO.File]::WriteAllText($svgPath, $svg, (New-Object Text.UTF8Encoding $false))
    '{0} → {1}（{2} × {3}）' -f $item.Name, (Split-Path $svgPath -Leaf), $w, $h
    if ($Png) { & (Join-Path $PSScriptRoot 'svg2png.ps1') -Svg $svgPath -Scale $Scale }
}
