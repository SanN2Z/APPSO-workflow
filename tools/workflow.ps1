[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet(
        "verify", "test", "repo-preflight", "capabilities", "validate", "image-preflight",
        "opening-check", "wechat", "company", "insight", "retrospective-init",
        "retrospective-audit", "corpus", "pdf-render", "crop-image", "normalize-text",
        "openrouter", "x-env", "x-readonly", "x-visibility", "x-post",
        "x-publish-queue", "x-trend-scan", "codex-company",
        "codex-company-feishu", "claude-ox", "set-openrouter-key"
    )]
    [string]$Command,

    [Parameter(Position = 1, ValueFromRemainingArguments = $true)]
    [string[]]$CommandArgs
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $PSScriptRoot "workflow-toolchain.json"
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$remainingArgs = if ($null -eq $CommandArgs) { @() } else { @($CommandArgs) }

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string[]]$NativeArgs
    )
    & $Executable @NativeArgs
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw ".venv is missing. Run: powershell -NoProfile -ExecutionPolicy Bypass -File tools/bootstrap.ps1"
}

Push-Location $repoRoot
try {
    if ($Command -eq "verify") {
        Invoke-Checked $python (@((Join-Path $PSScriptRoot "verify_clone_ready.py")) + $remainingArgs)
        exit 0
    }

    if ($Command -eq "test") {
        $selectedTests = if ($remainingArgs.Count -gt 0 -and -not $remainingArgs[0].StartsWith('-')) {
            $remainingArgs
        }
        else {
            @($manifest.test_paths) + $remainingArgs
        }
        $testArgs = @("-m", "pytest", "-q") + $selectedTests
        Invoke-Checked $python $testArgs
        exit 0
    }

    if ($Command -in @("codex-company", "codex-company-feishu")) {
        $launcher = Join-Path $repoRoot $manifest.powershell_entrypoints.PSObject.Properties[$Command].Value
        if ($remainingArgs.Count -gt 0) {
            & $launcher -CodexArgs $remainingArgs
        }
        else {
            & $launcher
        }
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
        exit 0
    }

    $powershellProperty = $manifest.powershell_entrypoints.PSObject.Properties[$Command]
    if ($null -ne $powershellProperty) {
        & (Join-Path $repoRoot $powershellProperty.Value) @remainingArgs
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
        exit 0
    }

    $entrypoint = $manifest.entrypoints.PSObject.Properties[$Command].Value
    if (-not $entrypoint) {
        throw "No entrypoint is registered for command: $Command"
    }
    Invoke-Checked $python (@((Join-Path $repoRoot $entrypoint)) + $remainingArgs)
}
finally {
    Pop-Location
}
