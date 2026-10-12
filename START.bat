@echo off
setlocal
cd /d "%~dp0"
if not exist "runtime\python.exe" (
  echo This launcher requires the Windows handoff package.
  echo For the GitHub source checkout, run setup.ps1 then start.ps1.
  pause
  exit /b 1
)
"runtime\python.exe" -E -s -X utf8 "tools\portable_launcher.py"
pause
