Write-Host "[Genesys Login Fix] Clearing cached token files..."
$tokenPath = "$env:LOCALAPPDATA\Genesys\AuthCache"
if (Test-Path $tokenPath) {
  Remove-Item -Path $tokenPath -Recurse -Force
  Write-Host "Cache removed: $tokenPath"
} else {
  Write-Host "No cache folder found."
}
Write-Host "Please relaunch Genesys workspace and sign in again."
