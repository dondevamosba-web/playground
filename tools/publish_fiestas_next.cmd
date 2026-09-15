@echo off
REM Silent wrapper: runs in background with no visible window
setlocal
set PYTHONIOENCODING=utf-8
cd /d "%~dp0.."
start /b /min "" ".venv-win\Scripts\python.exe" "tools\publish_fiestas_next.py" --only-flyers >> ".tmp\fiestas_publish.log" 2>&1
endlocal
