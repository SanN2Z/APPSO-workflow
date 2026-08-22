<#
.SYNOPSIS
    在一个独立沙盒目录里，用 OpenRouter 的 stealth/ox-alpha 驱动 Claude Code。
.DESCRIPTION
    OpenRouter 提供原生 Anthropic 格式端点 /api/v1/messages，不需要转换代理，
    直接把 ANTHROPIC_BASE_URL 指过去即可。

    环境变量只在本脚本启动的这个进程里生效，退出即失效。
    工作目录默认是仓库外的独立沙盒，隐身模型看不到自媒体运营仓库的任何内容。
.EXAMPLE
    .\tools\claude-ox.ps1
    .\tools\claude-ox.ps1 -WorkDir (Join-Path $env:TEMP "myplayground")
    .\tools\claude-ox.ps1 -Isolated                 # 连全局 CLAUDE.md / skills 也不加载
    .\tools\claude-ox.ps1 -ClaudeArgs @('-p','写个快排')   # 透传参数给 claude（headless）
#>
[CmdletBinding()]
param(
    [string]$WorkDir = "",
    [string]$Model = "stealth/ox-alpha",
    [switch]$Isolated,
    [switch]$SkipCheck,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ClaudeArgs
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 > $null

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$claudeCommand = Join-Path $repoRoot 'tools\agent-runtime\node_modules\.bin\claude.cmd'
if ([string]::IsNullOrWhiteSpace($WorkDir)) {
    $WorkDir = Join-Path ([System.IO.Path]::GetTempPath()) "ox-alpha-lab"
}

# ---------- 1. 取 key（只从仓库 .env 读，key 不会发给模型） ----------
$key = $env:OPENROUTER_API_KEY
if ([string]::IsNullOrWhiteSpace($key)) {
    $envPath = Join-Path $repoRoot '.env'
    if (Test-Path $envPath) {
        foreach ($line in [System.IO.File]::ReadAllLines($envPath)) {
            if ($line -match '^\s*OPENROUTER_API_KEY\s*=\s*(.+)$') {
                $key = $Matches[1].Trim().Trim('"').Trim("'")
                break
            }
        }
    }
}
if ([string]::IsNullOrWhiteSpace($key)) {
    Write-Host "[fail] 没找到 OPENROUTER_API_KEY，先跑 .\tools\set_openrouter_key.ps1" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path -LiteralPath $claudeCommand -PathType Leaf)) {
    Write-Host "[fail] clone 内没有 Claude Code，请先运行 tools/bootstrap.ps1。" -ForegroundColor Red
    exit 1
}

# ---------- 2. 准备沙盒目录 ----------
$sandboxCreated = $false
if (-not (Test-Path $WorkDir)) {
    New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null
    $sandboxCreated = $true
}
$WorkDir = (Resolve-Path $WorkDir).Path

# 沙盒必须在仓库外，否则隐身模型能读到稿件和选题
if ($WorkDir.StartsWith($repoRoot, [StringComparison]::OrdinalIgnoreCase)) {
    Write-Host "[fail] 沙盒目录 $WorkDir 在仓库 $repoRoot 内部。" -ForegroundColor Red
    Write-Host "       隐身模型的 prompt 会回传给模型提供方，换个仓库外的路径。" -ForegroundColor Red
    exit 1
}

$readme = Join-Path $WorkDir 'README.md'
if ($sandboxCreated -and -not (Test-Path $readme)) {
    $readmeText = @"
# ox-alpha 沙盒

用 ``自媒体运营\tools\claude-ox.ps1`` 启动的隐身模型试验场。

**注意**：这里的一切内容都会随 prompt 发给 OpenRouter 上的匿名模型提供方。
不要往这个目录放稿件、选题、客户资料或任何未公开的东西。
"@
    [System.IO.File]::WriteAllText($readme, $readmeText, (New-Object System.Text.UTF8Encoding($false)))
}

# ---------- 3. 启动前 ping 一次端点 ----------
if (-not $SkipCheck) {
    Write-Host "[info] 探测 $Model ..." -ForegroundColor DarkGray
    $body = @{
        model      = $Model
        max_tokens = 16
        messages   = @(@{ role = "user"; content = "ping" })
    } | ConvertTo-Json -Depth 6 -Compress
    try {
        $resp = Invoke-RestMethod -Uri "https://openrouter.ai/api/v1/messages" -Method Post `
            -Headers @{ "Authorization" = "Bearer $key"; "anthropic-version" = "2023-06-01" } `
            -ContentType "application/json" -Body $body -TimeoutSec 60
        Write-Host "[ok] 端点可用，模型返回 model=$($resp.model)" -ForegroundColor Green
    } catch {
        Write-Host "[fail] 端点探测失败：$($_.Exception.Message)" -ForegroundColor Red
        Write-Host "       模型 id 可能已下线/改名，去 https://openrouter.ai/models 确认。" -ForegroundColor Red
        Write-Host "       确定要硬闯可以加 -SkipCheck。" -ForegroundColor DarkGray
        exit 1
    }
}

# ---------- 4. 只在本进程内注入环境变量 ----------
# 用 AUTH_TOKEN 而不是 API_KEY：前者发 Authorization: Bearer，OpenRouter 认这个
$env:ANTHROPIC_BASE_URL   = "https://openrouter.ai/api"
$env:ANTHROPIC_AUTH_TOKEN = $key
Remove-Item Env:\ANTHROPIC_API_KEY -ErrorAction SilentlyContinue

# /model 的三档全部指向同一个模型，免得切档时打到不存在的 id
$env:ANTHROPIC_MODEL                = $Model
$env:ANTHROPIC_SMALL_FAST_MODEL     = $Model
$env:ANTHROPIC_DEFAULT_OPUS_MODEL   = $Model
$env:ANTHROPIC_DEFAULT_SONNET_MODEL = $Model
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL  = $Model

$env:API_TIMEOUT_MS = "600000"
$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"

if ($Isolated) {
    $env:CLAUDE_CONFIG_DIR = Join-Path $env:USERPROFILE ".claude-ox"
    if (-not (Test-Path $env:CLAUDE_CONFIG_DIR)) {
        New-Item -ItemType Directory -Path $env:CLAUDE_CONFIG_DIR -Force | Out-Null
    }
}

Write-Host ""
Write-Host "  模型      : $Model" -ForegroundColor Cyan
Write-Host "  端点      : $env:ANTHROPIC_BASE_URL/v1/messages" -ForegroundColor Cyan
Write-Host "  工作目录  : $WorkDir" -ForegroundColor Cyan
if ($sandboxCreated) {
    Write-Host "              (新建的空沙盒)" -ForegroundColor DarkGray
}
if ($Isolated) {
    Write-Host "  配置目录  : $env:CLAUDE_CONFIG_DIR （全局 CLAUDE.md / skills 不加载）" -ForegroundColor Yellow
} else {
    Write-Host "  配置目录  : 默认 ~/.claude（全局 CLAUDE.md 会随 prompt 发给模型，想完全干净加 -Isolated）" -ForegroundColor DarkGray
}
Write-Host "  作用范围  : 仅本窗口本进程，退出即失效，不影响你平时的 claude" -ForegroundColor DarkGray
Write-Host "  已知缺陷  : count_tokens 端点 404，/context 精确计数可能报错，不影响对话" -ForegroundColor DarkGray
Write-Host ""

# ---------- 5. 在沙盒里启动 ----------
Push-Location $WorkDir
try {
    if ($ClaudeArgs -and $ClaudeArgs.Count -gt 0) {
        & $claudeCommand @ClaudeArgs
    } else {
        & $claudeCommand
    }
} finally {
    Pop-Location
}
