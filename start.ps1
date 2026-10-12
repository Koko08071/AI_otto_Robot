$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (!(Test-Path '.venv/Scripts/python.exe')) { throw 'Run setup.ps1 first.' }
& ./.venv/Scripts/python.exe web/server.py
exit $LASTEXITCODE
