@echo off
setlocal
cd /d "%~dp0"
"runtime\python.exe" -E -s -X utf8 "tools\check_environment.py"
pause
