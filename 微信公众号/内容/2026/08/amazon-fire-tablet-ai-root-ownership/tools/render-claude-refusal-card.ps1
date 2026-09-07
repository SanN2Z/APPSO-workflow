param(
    [Parameter(Mandatory = $true)]
    [string]$PackagePath
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$resolvedPackage = (Resolve-Path -LiteralPath $PackagePath).Path
$target = Join-Path $resolvedPackage "assets/author-claude-cyber-refusals-card.png"
if (-not $target.StartsWith($resolvedPackage, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Output path escaped the content package."
}
if (Test-Path -LiteralPath $target) {
    throw "Refusing to overwrite existing card: $target"
}

$bitmap = New-Object System.Drawing.Bitmap 1200, 760
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$graphics.Clear([System.Drawing.Color]::FromArgb(20, 24, 29))

$orange = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 184, 0))
$white = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(245, 247, 249))
$muted = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(164, 171, 180))
$panel = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(31, 37, 44))
$rule = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(67, 75, 84)), 2
$titleFont = New-Object System.Drawing.Font "Segoe UI Semibold", 28, ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
$numberFont = New-Object System.Drawing.Font "Segoe UI Semibold", 48, ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
$quoteFont = New-Object System.Drawing.Font "Segoe UI", 40, ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
$metaFont = New-Object System.Drawing.Font "Segoe UI", 24, ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)

$graphics.FillRectangle($orange, 0, 0, 1200, 64)
$graphics.DrawString("CLAUDE SAFEGUARD", $titleFont, [System.Drawing.Brushes]::Black, 52, 14)

$graphics.FillRectangle($panel, 52, 112, 1096, 214)
$graphics.DrawString("01", $numberFont, $orange, 86, 162)
$graphics.DrawLine($rule, 200, 150, 200, 288)
$graphics.DrawString("Fable 5's safeguards flagged this message.", $quoteFont, $white, 246, 182)

$graphics.FillRectangle($panel, 52, 354, 1096, 214)
$graphics.DrawString("02", $numberFont, $orange, 86, 404)
$graphics.DrawLine($rule, 200, 392, 200, 530)
$graphics.DrawString("API Error: Opus 4.8's safeguards", $quoteFont, $white, 246, 406)
$graphics.DrawString("flagged this message.", $quoteFont, $white, 246, 466)

$graphics.DrawString("Source: Eric Pardee | fire-hd-ownership", $metaFont, $muted, 52, 672)
$graphics.FillRectangle($orange, 52, 718, 140, 6)

$bitmap.Save($target, [System.Drawing.Imaging.ImageFormat]::Png)

$titleFont.Dispose()
$numberFont.Dispose()
$quoteFont.Dispose()
$metaFont.Dispose()
$orange.Dispose()
$white.Dispose()
$muted.Dispose()
$panel.Dispose()
$rule.Dispose()
$graphics.Dispose()
$bitmap.Dispose()

Write-Output $target
