$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$OutputEncoding = [Console]::OutputEncoding
$root = $PSScriptRoot
$linuxPath = (wsl -d openEuler -- wslpath -a $root).Trim()
if ($LASTEXITCODE -ne 0) { throw "Cannot convert the project path for WSL" }
wsl -d openEuler -- python3 "$linuxPath/tools/verify_linux.py"
if ($LASTEXITCODE -ne 0) { throw "Verification failed. See logs/verification.log" }
