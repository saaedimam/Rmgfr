$ErrorActionPreference = "Stop"
Write-Host "Sanity: checking deploy & verify scripts..."
if (-not (Test-Path "platform\railway-deploy.ps1")) { throw "missing platform\railway-deploy.ps1" }
if (-not (Test-Path "platform\railway-deploy.sh")) { throw "missing platform\railway-deploy.sh" }
if (-not (Test-Path "platform\verify-deployment.js")) { throw "missing platform\verify-deployment.js" }
Write-Host "OK"
