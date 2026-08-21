@echo off
REM Silent wrapper: runs in background with no visible window
setlocal
set PYTHONIOENCODING=utf-8
cd /d "%~dp0.."
if "%~1"=="" (
  exit /b 1
)
start /b /min "" ".venv-win\Scripts\python.exe" "tools\publish_account.py" --account %1 >> ".tmp\publish_%1.log" 2>&1
endlocal
