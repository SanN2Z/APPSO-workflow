[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$workspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $workspaceRoot

try {
    $insideWorkTree = git rev-parse --is-inside-work-tree 2>$null
    if ($LASTEXITCODE -ne 0 -or $insideWorkTree -ne 'true') {
        throw 'Not inside a Git worktree.'
    }

    $candidatePaths = @(git -c core.quotepath=false ls-files --cached --others --exclude-standard)
    if ($LASTEXITCODE -ne 0) {
        throw 'Cannot enumerate Git candidate files.'
    }

    # Keep this script ASCII-only so Windows PowerShell 5 can parse it without a BOM.
    # .NET regular expressions decode the \u sequences when matching Unicode paths.
    $blockedPatterns = @(
        '(^|/)\.env$',
        '(^|/)\.env\..*\.local$',
        '(^|/)node_modules/',
        '(^|/)\.wenyan-runtime/',
        '(^|/)dist/',
        '^output/',
        '^\u4e34\u65f6\u7d20\u6750/',
        '^\.playwright-mcp/',
        '^\.tmp/',
        '^\.tmp-[^/]+/',
        '^APPSO-\u6570\u5b57\u8d44\u4ea7/01-\u680f\u76ee\u4e0e\u54c1\u724c/\u54c1\u724c\u89c6\u89c9/\u539f\u59cb\u8d44\u6599/',
        '^APPSO-\u6570\u5b57\u8d44\u4ea7/01-\u680f\u76ee\u4e0e\u54c1\u724c/\u54c1\u724c\u89c6\u89c9/\u751f\u56fe-Prompt/',
        '^APPSO-\u6570\u5b57\u8d44\u4ea7/90-\u53d7\u9650\u8d44\u6599/(?!README\.md$)'
    )

    $blockedFiles = foreach ($path in $candidatePaths) {
        $normalizedPath = $path -replace '\\', '/'
        foreach ($pattern in $blockedPatterns) {
            if ($normalizedPath -match $pattern) {
                $path
                break
            }
        }
    }

    if ($blockedFiles) {
        Write-Error ("Files outside the Git boundary were found:`n" + (($blockedFiles | Sort-Object -Unique) -join "`n"))
    }

    $secretPattern = 'sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|Bearer\s+[A-Za-z0-9._~+/-]{24,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'
    $secretMatches = @(rg -n --hidden --glob '!.git/**' --glob '!*.png' --glob '!*.jpg' --glob '!*.jpeg' --glob '!*.gif' --glob '!*.mp4' --glob '!*.pdf' $secretPattern . 2>$null)
    $rgExitCode = $LASTEXITCODE
    if ($rgExitCode -gt 1) {
        throw 'Secret scan failed to execute.'
    }
    if ($secretMatches) {
        Write-Error ("Possible credentials require review:`n" + ($secretMatches -join "`n"))
    }

    $diffCheck = @(git diff --check 2>&1)
    if ($LASTEXITCODE -ne 0) {
        Write-Error ("git diff --check failed:`n" + ($diffCheck -join "`n"))
    }

    $stagedDiffCheck = @(git diff --cached --check 2>&1)
    if ($LASTEXITCODE -ne 0) {
        Write-Error ("git diff --cached --check failed:`n" + ($stagedDiffCheck -join "`n"))
    }

    $candidateFiles = foreach ($path in $candidatePaths) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            Get-Item -LiteralPath $path
        }
    }
    $totalBytes = ($candidateFiles | Measure-Object -Property Length -Sum).Sum
    if ($null -eq $totalBytes) {
        $totalBytes = 0
    }
    $largeFiles = @($candidateFiles | Where-Object { $_.Length -gt 50MB } | Sort-Object Length -Descending)
    if ($largeFiles) {
        Write-Error ("Candidate files larger than 50 MB require review:`n" + (($largeFiles | ForEach-Object { $_.FullName }) -join "`n"))
    }

    Write-Host ('[pass] {0} candidate files, {1:N2} MB total.' -f $candidateFiles.Count, ($totalBytes / 1MB))
    Write-Host '[pass] Git boundary, common credential, large-file, unstaged diff, and staged diff checks passed.'
}
finally {
    Pop-Location
}
