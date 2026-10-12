@echo off
setlocal
cd /d "%~dp0"
if not exist "runtime\python.exe" (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "tools\bootstrap_runtime.ps1"
  if errorlevel 1 (
    pause
    exit /b 1
  )
)
"runtime\python.exe" -E -s -X utf8 "tools\portable_launcher.py"
pause
