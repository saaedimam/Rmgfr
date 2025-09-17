$SOFT = 10MB
$HARD = 50MB
$status = 0

git ls-files | ForEach-Object {
    if (Test-Path -LiteralPath $_) {
        $size = (Get-Item -LiteralPath $_).Length
        if ($size -ge $HARD) {
            Write-Host "ERROR: $_ is $([math]::Round($size/1MB, 2)) MB (>50MB). Use Git LFS." -ForegroundColor Red
            $status = 1
        } elseif ($size -ge $SOFT) {
            Write-Host "WARN: $_ is $([math]::Round($size/1MB, 2)) MB (>10MB). Consider Git LFS." -ForegroundColor Yellow
        }
    }
}

exit $status
