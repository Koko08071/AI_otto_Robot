param([string]$Archive = '')
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$projectRoot = Split-Path $PSScriptRoot -Parent
$manifest = Get-Content -LiteralPath (Join-Path $projectRoot 'release-assets.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$asset = $manifest.windows
if (!$asset.sha256 -or $asset.sha256.Length -ne 64) { throw 'Release manifest is not ready.' }
if (!$Archive) {
    $cache = Join-Path $projectRoot '.downloads'
    New-Item -ItemType Directory -Force -Path $cache | Out-Null
    $Archive = Join-Path $cache $asset.name
    if (!(Test-Path -LiteralPath $Archive)) {
        Write-Host 'First launch: downloading the complete Windows runtime from GitHub. This may take several minutes.'
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $partial = "$Archive.download"
        Invoke-WebRequest -Uri $asset.url -OutFile $partial -UseBasicParsing
        Move-Item -LiteralPath $partial -Destination $Archive
    }
}
if ((Get-FileHash -LiteralPath $Archive -Algorithm SHA256).Hash.ToLower() -ne $asset.sha256) { throw 'Archive checksum failed. Download the release again.' }
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [IO.Compression.ZipFile]::OpenRead((Resolve-Path -LiteralPath $Archive).Path)
try {
    foreach ($item in $zip.Entries) {
        $relative = $item.FullName -replace '^[^/]+/', ''
        if ($relative -notmatch '^(runtime|models|voice-model)/' -or $item.FullName.EndsWith('/')) { continue }
        $target = [IO.Path]::GetFullPath((Join-Path $projectRoot $relative))
        $allowed = @('runtime', 'models', 'voice-model') | Where-Object { $target.StartsWith((Join-Path $projectRoot $_) + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) }
        if (!$allowed) { throw 'Invalid archive path.' }
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($target)) | Out-Null
        [IO.Compression.ZipFileExtensions]::ExtractToFile($item, $target, $true)
    }
} finally { $zip.Dispose() }
& (Join-Path $projectRoot 'runtime\python.exe') -E -s -X utf8 (Join-Path $projectRoot 'tools\check_environment.py')
if ($LASTEXITCODE -ne 0) { throw 'Runtime validation failed.' }
Write-Host 'Runtime ready. Opening Otto Studio...'
