param(
    [Parameter(Mandatory = $true)]
    [string]$PackagePath
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$resolvedPackage = (Resolve-Path -LiteralPath $PackagePath).Path
$outputDir = Join-Path $resolvedPackage "research/source-assets"
if (-not $outputDir.StartsWith($resolvedPackage, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Output directory escaped the content package."
}
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$cards = @(
    @{
        File = "hn-comment-fame-promise-49409832.png"
        Author = "Shuddown"
        Id = "49409832"
        Quote = "So all we need to get models to hack hardened devices is the promise of fame on Hacker News."
    },
    @{
        File = "hn-comment-iphone-jailbreak-49409918.png"
        Author = "sajithdilshan"
        Id = "49409918"
        Quote = "I wonder, in the not so distant future if we would have jailbreak for iPhones again thanks to AI. That would be glorious."
    }
)

function Draw-WrappedText {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Text,
        [System.Drawing.Font]$Font,
        [System.Drawing.Brush]$Brush,
        [float]$X,
        [float]$Y,
        [float]$MaxWidth,
        [float]$LineHeight
    )

    $words = $Text.Split(" ")
    $line = ""
    $cursorY = $Y
    foreach ($word in $words) {
        $candidate = if ($line) { "$line $word" } else { $word }
        if ($Graphics.MeasureString($candidate, $Font).Width -le $MaxWidth) {
            $line = $candidate
            continue
        }
        $Graphics.DrawString($line, $Font, $Brush, $X, $cursorY)
        $cursorY += $LineHeight
        $line = $word
    }
    if ($line) {
        $Graphics.DrawString($line, $Font, $Brush, $X, $cursorY)
        $cursorY += $LineHeight
    }
    return $cursorY
}

foreach ($card in $cards) {
    $target = Join-Path $outputDir $card.File
    if (Test-Path -LiteralPath $target) {
        throw "Refusing to overwrite existing card: $target"
    }

    $bitmap = New-Object System.Drawing.Bitmap 1200, 760
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $graphics.Clear([System.Drawing.Color]::FromArgb(246, 246, 239))

    $orange = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 102, 0))
    $ink = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(28, 28, 28))
    $muted = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(105, 105, 105))
    $white = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::White)
    $quoteFont = New-Object System.Drawing.Font "Segoe UI", 35, ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
    $metaFont = New-Object System.Drawing.Font "Segoe UI", 25, ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
    $labelFont = New-Object System.Drawing.Font "Segoe UI Semibold", 24, ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
    $markFont = New-Object System.Drawing.Font "Georgia", 88, ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)

    $graphics.FillRectangle($orange, 0, 0, 1200, 58)
    $graphics.DrawString("Hacker News comment", $labelFont, $white, 58, 14)
    $graphics.DrawString('"', $markFont, $orange, 58, 100)
    [void](Draw-WrappedText -Graphics $graphics -Text $card.Quote -Font $quoteFont -Brush $ink -X 120 -Y 190 -MaxWidth 950 -LineHeight 58)

    $meta = "$($card.Author)  |  comment $($card.Id)"
    $graphics.DrawString($meta, $metaFont, $muted, 120, 640)
    $graphics.FillRectangle($orange, 120, 700, 110, 6)

    $bitmap.Save($target, [System.Drawing.Imaging.ImageFormat]::Png)

    $quoteFont.Dispose()
    $metaFont.Dispose()
    $labelFont.Dispose()
    $markFont.Dispose()
    $orange.Dispose()
    $ink.Dispose()
    $muted.Dispose()
    $white.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()

    Write-Output $target
}
