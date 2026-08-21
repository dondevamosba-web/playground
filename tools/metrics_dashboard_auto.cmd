@echo off
REM Auto-refresh metrics dashboard. Runs every 24h at 3 AM.
setlocal
set PYTHONIOENCODING=utf-8
cd /d "%~dp0.."
".venv-win\Scripts\python.exe" "tools\metrics_dashboard_auto.py" >> ".tmp\metrics_auto.log" 2>&1
endlocal
