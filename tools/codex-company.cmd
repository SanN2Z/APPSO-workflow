@echo off
setlocal

rem Keep the company Codex account, configuration, sessions, and MCPs isolated.
set "CODEX_HOME=%USERPROFILE%\.codex-company"

if not exist "%CODEX_HOME%" (
    mkdir "%CODEX_HOME%" || exit /b 1
)

call "%APPDATA%\npm\codex.cmd" %*
set "CODEX_COMPANY_EXIT_CODE=%ERRORLEVEL%"

endlocal & exit /b %CODEX_COMPANY_EXIT_CODE%
