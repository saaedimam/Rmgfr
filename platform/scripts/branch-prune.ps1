param([string]$RepoDir = ".")

Set-Location $RepoDir -ErrorAction SilentlyContinue

Write-Host "Fetching and pruning remote branches..."
git fetch --all --prune

Write-Host "Finding merged branches..."
$protected = @('main', 'master', 'develop', 'dev', 'beta', 'canary')
$mergedBranches = git branch --merged main 2>$null | ForEach-Object { $_.Trim() -replace '^\* ', '' } | Where-Object { $_ -and $_ -notin $protected }

if ($mergedBranches) {
    Write-Host "Deleting merged branches: $($mergedBranches -join ', ')"
    $mergedBranches | ForEach-Object { git branch -d $_ }
} else {
    Write-Host "No merged branches to delete"
}

Write-Host "Pruning remote references..."
git remote prune origin 2>$null

Write-Host "Optimizing repository..."
git gc --prune=now --aggressive 2>$null
git repack -Ad 2>$null

Write-Host "Branch pruning complete"
