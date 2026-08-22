@echo off
setlocal

rem Delegate to the clone-local PowerShell launcher and pinned Codex runtime.
if "%~1"=="" (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0codex-company.ps1"
) else (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0codex-company.ps1" -CodexArgs %*
)
set "CODEX_COMPANY_EXIT_CODE=%ERRORLEVEL%"

endlocal & exit /b %CODEX_COMPANY_EXIT_CODE%
