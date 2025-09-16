# PowerShell version of guard-big-files.sh
# Fail on any file > 50MB (hard limit) or warn > 10MB (soft).

$SOFT = 10MB
$HARD = 50MB
$status = 0

$files = git ls-files -z | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }

foreach ($file in $files) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        if ($size -ge $HARD) {
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Error "ERROR: $file is $sizeMB MB (> 50MB). Use Git LFS."
            $status = 1
        } elseif ($size -ge $SOFT) {
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Warning "WARN: $file is $sizeMB MB (> 10MB). Consider Git LFS."
        }
    }
}

exit $status
