@echo off
setlocal
set PYTHONIOENCODING=utf-8
cd /d "C:\Users\Guido\Dropbox\playground"
C:\Users\Guido\Dropbox\playground\.venv-win\Scripts\python.exe "C:\Users\Guido\Dropbox\playground\tools\retention_analysis.py" >> ".tmp\retention.log" 2>&1
endlocal
