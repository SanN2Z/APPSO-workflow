[CmdletBinding()]
param(
    [switch]$WithFeishu,
    [switch]$ImportUatFromClipboard,
    [string]$CodexHome = "",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CodexArgs
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$codexCommand = Join-Path $repoRoot "tools\agent-runtime\node_modules\.bin\codex.cmd"
$configTemplate = Join-Path $repoRoot "tools\capability-templates\codex-company.config.toml"
$envFile = Join-Path $repoRoot ".env"

if ([string]::IsNullOrWhiteSpace($CodexHome)) {
    $CodexHome = Join-Path $repoRoot ".local-capabilities\codex-company"
}

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

function Read-DotEnvValue {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Name
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    foreach ($line in [IO.File]::ReadAllLines($Path)) {
        if ($line -match ("^\s*" + [regex]::Escape($Name) + "\s*=\s*(.*)$")) {
            return $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
    return $null
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

if (-not (Test-Path -LiteralPath $codexCommand -PathType Leaf)) {
    throw "Clone-local Codex is missing. Run tools/bootstrap.ps1 first."
}
if (-not (Test-Path -LiteralPath $configTemplate -PathType Leaf)) {
    throw "Company Codex config template is missing: $configTemplate"
}

$CodexHome = [IO.Path]::GetFullPath($CodexHome)
$configPath = Join-Path $CodexHome "config.toml"
if (-not (Test-Path -LiteralPath $CodexHome -PathType Container)) {
    New-Item -ItemType Directory -Path $CodexHome -Force | Out-Null
}
if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    Copy-Item -LiteralPath $configTemplate -Destination $configPath
}

$uat = $null
$previousCodexHome = $env:CODEX_HOME
$previousFeishuUat = $env:FEISHU_MCP_UAT
$exitCode = 1
try {
    if ($WithFeishu) {
        $uat = Find-FeishuUat -Text $env:FEISHU_MCP_UAT
        if ($null -eq $uat -and $ImportUatFromClipboard) {
            $uat = Find-FeishuUat -Text (Get-Clipboard -Raw)
            if ($null -ne $uat) {
                Save-FeishuUat -Path $envFile -Value $uat
                Set-Clipboard -Value " "
            }
        }
        if ($null -eq $uat) {
            $uat = Find-FeishuUat -Text (Read-DotEnvValue -Path $envFile -Name "FEISHU_MCP_UAT")
        }
        if ($null -eq $uat) {
            throw "No complete FEISHU_MCP_UAT was found in the process, local .env, or clipboard."
        }
        $env:FEISHU_MCP_UAT = $uat
    }

    $env:CODEX_HOME = $CodexHome
    Set-Location -LiteralPath $repoRoot
    Write-Host "Using clone-local Codex and company config: $configPath"
    & $codexCommand @CodexArgs
    $exitCode = $LASTEXITCODE
}
finally {
    if ($null -eq $previousCodexHome) {
        Remove-Item Env:CODEX_HOME -ErrorAction SilentlyContinue
    }
    else {
        $env:CODEX_HOME = $previousCodexHome
    }
    if ($null -eq $previousFeishuUat) {
        Remove-Item Env:FEISHU_MCP_UAT -ErrorAction SilentlyContinue
    }
    else {
        $env:FEISHU_MCP_UAT = $previousFeishuUat
    }
    $uat = $null
}

exit $exitCode
