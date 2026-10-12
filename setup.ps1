param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (!(Test-Path '.venv/Scripts/python.exe')) {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 first.' }
}
& ./.venv/Scripts/python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
if (!(Test-Path config.local.json)) { Copy-Item config.example.json config.local.json }
Write-Host 'Edit config.local.json, then run start.ps1. Models: .venv/Scripts/python.exe tools/download_models.py'
