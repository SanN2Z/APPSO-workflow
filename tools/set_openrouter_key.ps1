# 交互式写入 OpenRouter API key 到仓库 .env（幂等，可重复跑）
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 > $null

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $repoRoot '.env'

Write-Host ""
Write-Host "把 OpenRouter API key 粘贴到下面，然后回车（输入不回显，看不见是正常的）:" -ForegroundColor Cyan
$secure = Read-Host -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $key = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

if ($null -eq $key) { $key = '' }
$key = $key.Trim()

if ([string]::IsNullOrWhiteSpace($key)) {
    Write-Host "[fail] 没输入内容，已中止，.env 未改动。" -ForegroundColor Red
    exit 1
}
if (-not $key.StartsWith('sk-or-')) {
    Write-Host "[warn] 这个 key 不是 sk-or- 开头，OpenRouter 的 key 通常是。仍然继续写入。" -ForegroundColor Yellow
}

# 读现有 .env（utf-8-sig 兼容 BOM）
$lines = @()
if (Test-Path $envPath) {
    $lines = [System.IO.File]::ReadAllLines($envPath, (New-Object System.Text.UTF8Encoding($true)))
    # 备份到系统临时目录，避免备份文件落进仓库被 git 追踪
    $backup = Join-Path $env:TEMP ("env-backup-" + (Get-Random) + ".txt")
    Copy-Item $envPath $backup -Force
    Write-Host "[info] 原 .env 已备份到 $backup" -ForegroundColor DarkGray
}

$newLine = "OPENROUTER_API_KEY=$key"
$found = $false
$out = New-Object System.Collections.Generic.List[string]
foreach ($line in $lines) {
    if ($line -match '^\s*OPENROUTER_API_KEY\s*=') {
        if (-not $found) {
            $out.Add($newLine)
            $found = $true
        }
        # 重复行直接丢弃，保证只剩一条
    } else {
        $out.Add($line)
    }
}
if (-not $found) { $out.Add($newLine) }

# 必须 UTF-8 无 BOM：PS 5.1 的 Out-File -Encoding utf8 会加 BOM，污染 .env 第一行的键名
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllLines($envPath, $out, $utf8NoBom)

$masked = $key.Substring(0, [Math]::Min(12, $key.Length)) + '****'
Write-Host ""
if ($found) {
    Write-Host "[ok] 已更新 $envPath 里的 OPENROUTER_API_KEY = $masked" -ForegroundColor Green
} else {
    Write-Host "[ok] 已追加到 $envPath : OPENROUTER_API_KEY = $masked" -ForegroundColor Green
}
Write-Host "     .env 已在 .gitignore 中，不会被提交。" -ForegroundColor DarkGray

# 顺手设进当前会话，这个窗口里可以直接用
$env:OPENROUTER_API_KEY = $key

Write-Host ""
Write-Host "[info] 自检 key 中..." -ForegroundColor Cyan
Push-Location $repoRoot
try {
    python tools/openrouter_chat.py --check
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "接着可以直接试模型:" -ForegroundColor Cyan
Write-Host '  python tools/openrouter_chat.py "用一句话说说你是什么模型"' -ForegroundColor White
