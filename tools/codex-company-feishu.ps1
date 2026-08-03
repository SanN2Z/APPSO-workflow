[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CodexArgs
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$codexCommand = Join-Path $env:APPDATA "npm\codex.cmd"
$companyCodexHome = Join-Path $env:USERPROFILE ".codex-company"
$envFile = Join-Path $repoRoot ".env"
$uat = $null
$exitCode = 1

function Find-FeishuUat {
    param([AllowNull()][string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return $null
    }

    $match = [regex]::Match(
        $Text,
        "(?<![A-Za-z0-9_-])([A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})(?![A-Za-z0-9_-])"
    )
    if (-not $match.Success -or $match.Groups[1].Value.Length -lt 100) {
        return $null
    }

    return $match.Groups[1].Value
}

function Save-FeishuUat {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Value
    )

    & git -C $repoRoot check-ignore -q .env
    if ($LASTEXITCODE -ne 0) {
        throw ".env is not ignored by Git; refusing to store the UAT."
    }

    $content = if (Test-Path -LiteralPath $Path) {
        [IO.File]::ReadAllText($Path)
    }
    else {
        ""
    }

    $line = "FEISHU_MCP_UAT=$Value"
    if ([regex]::IsMatch($content, "(?m)^\s*FEISHU_MCP_UAT\s*=.*$")) {
        $content = [regex]::Replace(
            $content,
            "(?m)^\s*FEISHU_MCP_UAT\s*=.*$",
            $line,
            1
        )
    }
    else {
        if ($content.Length -gt 0 -and -not $content.EndsWith("`n")) {
            $content += [Environment]::NewLine
        }
        $content += $line + [Environment]::NewLine
    }

    [IO.File]::WriteAllText($Path, $content, [Text.UTF8Encoding]::new($false))
}

try {
    if (-not (Test-Path -LiteralPath $codexCommand -PathType Leaf)) {
        throw "Codex CLI was not found: $codexCommand"
    }

    $clipboardText = Get-Clipboard -Raw
    $uat = Find-FeishuUat -Text $clipboardText
    if ($null -ne $uat) {
        Save-FeishuUat -Path $envFile -Value $uat
        Set-Clipboard -Value " "
    }

    if ($null -eq $uat -and (Test-Path -LiteralPath $envFile -PathType Leaf)) {
        $uat = Find-FeishuUat -Text ([IO.File]::ReadAllText($envFile))
    }

    if ($null -eq $uat) {
        throw "No complete Feishu user_access_token was found in the clipboard or local .env."
    }

    $env:CODEX_HOME = $companyCodexHome
    $env:FEISHU_MCP_UAT = $uat

    Set-Location -LiteralPath $repoRoot
    Write-Host "Feishu UAT loaded from local .env or refreshed from the clipboard."
    Write-Host "After startup, run /mcp verbose and inspect feishu_docs."

    & $codexCommand @CodexArgs
    $exitCode = $LASTEXITCODE
}
finally {
    Remove-Item Env:FEISHU_MCP_UAT -ErrorAction SilentlyContinue
    $uat = $null
}

exit $exitCode
