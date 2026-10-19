[CmdletBinding()]
param(
    [switch]$CheckOnly,
    [switch]$FullTest,
    [string]$PythonCommand = "python"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $PSScriptRoot "workflow-toolchain.json"
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$venvRoot = Join-Path $repoRoot ".venv"
$venvPython = Join-Path $venvRoot "Scripts\python.exe"
$verifier = Join-Path $PSScriptRoot "verify_clone_ready.py"
$capabilityManager = Join-Path $repoRoot $manifest.entrypoints.capabilities
$requirements = Join-Path $repoRoot $manifest.python.requirements_file

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string[]]$NativeArgs
    )
    & $Executable @NativeArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $Executable"
    }
}

Push-Location $repoRoot
try {
    if (-not $CheckOnly) {
        Write-Output "[bootstrap] Checking tracked source contract..."
        Invoke-Checked $PythonCommand @($verifier, "--source-only")

        if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
            if (Test-Path -LiteralPath $venvRoot) {
                throw ".venv exists but Scripts/python.exe is missing. Move or remove that incomplete local directory, then retry."
            }
            Write-Output "[bootstrap] Creating .venv..."
            Invoke-Checked $PythonCommand @("-m", "venv", $venvRoot)
        }

        Write-Output "[bootstrap] Installing pinned Python dependencies..."
        Invoke-Checked $venvPython @("-m", "pip", "install", "--disable-pip-version-check", "-r", $requirements)

        $npmCommand = Get-Command "npm.cmd" -ErrorAction SilentlyContinue
        if (-not $npmCommand) {
            $npmCommand = Get-Command "npm" -ErrorAction SilentlyContinue
        }
        if (-not $npmCommand) {
            throw "npm was not found. Install the Node version recorded in .nvmrc, then retry."
        }
        foreach ($installation in $manifest.node.installations) {
            $nodeRoot = Join-Path $repoRoot $installation.package_root
            Write-Output "[bootstrap] Installing locked Node dependencies: $($installation.id)..."
            Invoke-Checked $npmCommand.Source @("--prefix", $nodeRoot, "ci", "--no-audit", "--no-fund")
        }

        Write-Output "[bootstrap] Preparing all clone-local capability configuration slots..."
        Invoke-Checked $venvPython @($capabilityManager, "prepare")
        Write-Output "[bootstrap] Restoring pinned project-local ARIS research skills..."
        Invoke-Checked $venvPython @((Join-Path $PSScriptRoot "aris_project.py"), "setup")
    }

    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
        throw ".venv is not initialized. Run tools/bootstrap.ps1 without -CheckOnly first."
    }

    Write-Output "[bootstrap] Verifying clone-local runtime..."
    Invoke-Checked $venvPython @($verifier)

    if ($FullTest) {
        $testArgs = @("-m", "pytest", "-q") + @($manifest.test_paths)
        Write-Output "[bootstrap] Running the full local regression suite..."
        Invoke-Checked $venvPython $testArgs
    }

    Write-Output "[bootstrap] Ready. All adapters are packaged; use tools/workflow.ps1 capabilities doctor for local inputs."
}
finally {
    Pop-Location
}
