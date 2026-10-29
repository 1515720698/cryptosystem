param([switch]$ReuseHardware)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$OutputEncoding = [Console]::OutputEncoding
if (-not $ReuseHardware) {
    & python -X utf8 "$PSScriptRoot\tools\verify_ukey.py"
    if ($LASTEXITCODE -ne 0) { throw 'UKey verification failed; see logs/ukey_results.json' }
}
$forward = $PSScriptRoot.Replace('\', '/')
$linux = '/mnt/' + $forward.Substring(0,1).ToLower() + $forward.Substring(2)
& wsl -d openEuler -- python3 "$linux/tools/verify_crosscheck.py"
if ($LASTEXITCODE -ne 0) { throw 'Cross-check failed; see logs/crosscheck.log' }
