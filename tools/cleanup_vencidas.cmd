@echo off
REM Mark expired posts as "vencida". Runs once per week.
setlocal
set PYTHONIOENCODING=utf-8
cd /d "%~dp0.."
".venv-win\Scripts\python.exe" "tools\cleanup_vencidas.py" --apply >> ".tmp\cleanup.log" 2>&1
endlocal
