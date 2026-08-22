[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CodexArgs
)

$ErrorActionPreference = "Stop"
$launcher = Join-Path $PSScriptRoot "codex-company.ps1"
& $launcher -WithFeishu -ImportUatFromClipboard -CodexArgs $CodexArgs
exit $LASTEXITCODE
