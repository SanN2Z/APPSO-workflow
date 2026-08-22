param(
    [Parameter(Mandatory = $true)]
    [string]$Source,

    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,

    [string]$Prefix = "03-ox-alpha-self-analysis-scroll",
    [int]$TargetHeight = 1450,
    [int]$MinimumHeight = 1050,
    [int]$MaximumHeight = 1900
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$outputPath = [System.IO.Path]::GetFullPath($OutputDirectory)
[System.IO.Directory]::CreateDirectory($outputPath) | Out-Null

$bitmap = [System.Drawing.Bitmap]::FromFile($sourcePath)

try {
    $background = $bitmap.GetPixel(0, $bitmap.Height - 1)
    $tolerance = 4

    function Test-BlankRow {
        param(
            [System.Drawing.Bitmap]$Image,
            [int]$Y,
            [System.Drawing.Color]$Background,
            [int]$Tolerance
        )

        for ($x = 0; $x -lt $Image.Width; $x += 3) {
            $pixel = $Image.GetPixel($x, $Y)
            if (
                [Math]::Abs([int]$pixel.R - [int]$Background.R) -gt $Tolerance -or
                [Math]::Abs([int]$pixel.G - [int]$Background.G) -gt $Tolerance -or
                [Math]::Abs([int]$pixel.B - [int]$Background.B) -gt $Tolerance
            ) {
                return $false
            }
        }

        return $true
    }

    $contentBottom = $bitmap.Height - 1
    while ($contentBottom -gt 0 -and (Test-BlankRow -Image $bitmap -Y $contentBottom -Background $background -Tolerance $tolerance)) {
        $contentBottom--
    }
    $contentBottom = [Math]::Min($bitmap.Height, $contentBottom + 55)

    $blankRuns = [System.Collections.Generic.List[object]]::new()
    $runStart = $null
    for ($y = 0; $y -lt $contentBottom; $y++) {
        $isBlank = Test-BlankRow -Image $bitmap -Y $y -Background $background -Tolerance $tolerance
        if ($isBlank -and $null -eq $runStart) {
            $runStart = $y
        } elseif (-not $isBlank -and $null -ne $runStart) {
            if (($y - $runStart) -ge 40) {
                $blankRuns.Add([pscustomobject]@{ Start = $runStart; End = $y - 1; Mid = [int](($runStart + $y - 1) / 2) })
            }
            $runStart = $null
        }
    }

    if ($null -ne $runStart -and ($contentBottom - $runStart) -ge 40) {
        $blankRuns.Add([pscustomobject]@{ Start = $runStart; End = $contentBottom - 1; Mid = [int](($runStart + $contentBottom - 1) / 2) })
    }

    $cuts = [System.Collections.Generic.List[int]]::new()
    $cuts.Add(0)
    $cursor = 0

    while (($contentBottom - $cursor) -gt $MaximumHeight) {
        $ideal = $cursor + $TargetHeight
        $lower = $cursor + $MinimumHeight
        $upper = [Math]::Min($cursor + $MaximumHeight, $contentBottom)
        $candidate = $blankRuns |
            Where-Object { $_.Mid -ge $lower -and $_.Mid -le $upper } |
            Sort-Object { [Math]::Abs($_.Mid - $ideal) } |
            Select-Object -First 1

        if ($null -eq $candidate) {
            $nextCut = $upper
        } else {
            $nextCut = $candidate.Mid
        }

        if ($nextCut -le $cursor) {
            throw "Unable to select a forward slice boundary after row $cursor."
        }

        $cuts.Add([int]$nextCut)
        $cursor = [int]$nextCut
    }

    $cuts.Add($contentBottom)

    $outputs = [System.Collections.Generic.List[object]]::new()
    for ($i = 0; $i -lt ($cuts.Count - 1); $i++) {
        $top = $cuts[$i]
        $height = $cuts[$i + 1] - $top
        $rectangle = [System.Drawing.Rectangle]::new(0, $top, $bitmap.Width, $height)
        $slice = $bitmap.Clone($rectangle, $bitmap.PixelFormat)
        try {
            $filename = "{0}-{1:D2}.png" -f $Prefix, ($i + 1)
            $destination = Join-Path $outputPath $filename
            $slice.Save($destination, [System.Drawing.Imaging.ImageFormat]::Png)
            $outputs.Add([pscustomobject]@{
                File = $filename
                Width = $slice.Width
                Height = $slice.Height
                Bytes = (Get-Item -LiteralPath $destination).Length
                Top = $top
            })
        } finally {
            $slice.Dispose()
        }
    }

    [pscustomobject]@{
        Source = $sourcePath
        Background = "#{0:X2}{1:X2}{2:X2}" -f $background.R, $background.G, $background.B
        ContentBottom = $contentBottom
        SliceCount = $outputs.Count
        Slices = $outputs
    } | ConvertTo-Json -Depth 4
} finally {
    $bitmap.Dispose()
}
