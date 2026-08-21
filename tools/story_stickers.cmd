@echo off
REM Apply story stickers config. Run after story publishes.
REM Can be called with: story_stickers.cmd [event_date] [url]
setlocal
set PYTHONIOENCODING=utf-8
cd /d "%~dp0.."
".venv-win\Scripts\python.exe" "tools\story_stickers.py" --apply %* >> ".tmp\story_stickers.log" 2>&1
endlocal
