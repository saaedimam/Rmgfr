New-Item -ItemType Directory -Force -Path ".secrets_quarantine" | Out-Null

# Simple entropy and common token scans (best-effort)
$patterns = @(
    "api_key",
    "secret",
    "token",
    "passwd",
    "password",
    "AKIA[0-9A-Z]{16}",
    "AIza[0-9A-Za-z_-]{35}"
)

$excludeExtensions = @("*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.mp4", "*.mov", "*.avi", "*.zip", "*.gz", "*.7z", "*.pdf", "*.psd")

git ls-files | Where-Object {
    $file = $_
    $shouldExclude = $false
    foreach ($ext in $excludeExtensions) {
        if ($file -like $ext) {
            $shouldExclude = $true
            break
        }
    }
    -not $shouldExclude
} | ForEach-Object {
    $file = $_
    if (Test-Path -LiteralPath $file) {
        $content = Get-Content -LiteralPath $file -Raw -ErrorAction SilentlyContinue
        if ($content) {
            foreach ($pattern in $patterns) {
                if ($content -match $pattern) {
                    Write-Host "POSSIBLE SECRET: $file" -ForegroundColor Red
                    break
                }
            }
        }
    }
}

Write-Host "If any offenders printed, move them to .secrets_quarantine/ and add to .env.example" -ForegroundColor Yellow
