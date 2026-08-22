[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet(
        "verify", "test", "repo-preflight", "validate", "image-preflight",
        "opening-check", "wechat", "company", "insight", "retrospective-init",
        "retrospective-audit", "corpus", "pdf-render", "crop-image", "normalize-text",
        "openrouter"
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
        $selectedTests = if ($remainingArgs.Count -gt 0) {
            $remainingArgs
        }
        else {
            @($manifest.test_paths)
        }
        $testArgs = @("-m", "pytest", "-q") + $selectedTests
        Invoke-Checked $python $testArgs
        exit 0
    }

    if ($Command -eq "repo-preflight") {
        & (Join-Path $PSScriptRoot "repository_preflight.ps1") @remainingArgs
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
