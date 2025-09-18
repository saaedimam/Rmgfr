param()

$ErrorActionPreference = "Stop"

function Assert-File($Path) {
  if (Test-Path $Path) { return @{ name=$Path; status="PASS"; note="" } }
  else { return @{ name=$Path; status="FAIL"; note="missing" } }
}

function Assert-JsonProp($File, $PropPath) {
  if (!(Test-Path $File)) { return @{ name="$File:$PropPath"; status="FAIL"; note="file missing" } }
  $json = Get-Content $File -Raw | ConvertFrom-Json
  $value = $json
  foreach ($p in $PropPath -split '\.') {
    if ($null -eq $value.$p) { return @{ name="$File:$PropPath"; status="FAIL"; note="prop missing" } }
    $value = $value.$p
  }
  return @{ name="$File:$PropPath"; status="PASS"; note="$value" }
}

function Assert-PackageScript($Name) {
  if (!(Test-Path package.json)) { return @{ name="package.json:scripts.$Name"; status="FAIL"; note="package.json missing" } }
  $p = Get-Content package.json -Raw | ConvertFrom-Json
  if ($p.scripts.$Name) { @{ name="pkg:scripts.$Name"; status="PASS"; note=$p.scripts.$Name } }
  else { @{ name="pkg:scripts.$Name"; status="FAIL"; note="script missing" } }
}

$results = @()

# 1) Node sanity
$nodeMajor = [int]((node -p "process.versions.node.split('.')[0]"))
$results += @{ name="Node >= 18"; status=($(if ($nodeMajor -ge 18) {"PASS"} else {"FAIL"})); note="Detected $nodeMajor" }

# 2) Must-have files
$results += Assert-File "tsconfig.json"
$results += Assert-File "vitest.config.ts"
$results += Assert-File ".eslintrc.json"
$results += Assert-File ".prettierrc.json"
$results += Assert-File ".editorconfig"
$results += Assert-File ".gitignore"
$results += Assert-File ".eslintignore"
$results += Assert-File "src\main.ts"
$results += Assert-File "src\lib.ts"
$results += Assert-File "test\lib.test.ts"

# 3) Critical tsconfig knobs
$results += Assert-JsonProp "tsconfig.json" "compilerOptions.baseUrl"
$results += Assert-JsonProp "tsconfig.json" "compilerOptions.paths.@/*"

# 4) Required scripts present
$results += Assert-PackageScript "dev"
$results += Assert-PackageScript "build"
$results += Assert-PackageScript "test"
$results += Assert-PackageScript "test:run"
$results += Assert-PackageScript "test:coverage"
$results += Assert-PackageScript "lint"
$results += Assert-PackageScript "format"

# 5) Install if needed (idempotent)
if (!(Test-Path "node_modules")) { npm ci 2>$null; if ($LASTEXITCODE -ne 0) { npm i } }

# 6) Lint + format check (non-destructive)
try {
  npx eslint . | Out-Null
  $results += @{ name="eslint run"; status="PASS"; note="" }
} catch {
  $results += @{ name="eslint run"; status="FAIL"; note=$_.Exception.Message }
}

try {
  npx prettier -v | Out-Null
  $results += @{ name="prettier present"; status="PASS"; note="" }
} catch {
  $results += @{ name="prettier present"; status="FAIL"; note="not installed?" }
}

# 7) Build
try {
  npm run --silent build | Out-Null
  if (Test-Path "dist\main.js") { $results += @{ name="build output"; status="PASS"; note="dist/main.js" } }
  else { $results += @{ name="build output"; status="FAIL"; note="dist/main.js missing" } }
} catch {
  $results += @{ name="build"; status="FAIL"; note=$_.Exception.Message }
}

# 8) Runtime smoke
try {
  $out = node dist/main.js 2>&1
  if ($out -match "sum:\s*5") { $results += @{ name="runtime smoke"; status="PASS"; note=$out.Trim() } }
  else { $results += @{ name="runtime smoke"; status="FAIL"; note=$out.Trim() } }
} catch {
  $results += @{ name="runtime smoke"; status="FAIL"; note=$_.Exception.Message }
}

# 9) Tests + coverage
try {
  npm run --silent test:run | Out-Null
  $results += @{ name="tests run"; status="PASS"; note="" }
} catch {
  $results += @{ name="tests run"; status="FAIL"; note=$_.Exception.Message }
}

try {
  npm run --silent test:coverage | Out-Null
  if (Test-Path "coverage\index.html") { $results += @{ name="coverage report"; status="PASS"; note="coverage/index.html" } }
  else { $results += @{ name="coverage report"; status="FAIL"; note="report missing" } }
} catch {
  $results += @{ name="coverage"; status="FAIL"; note=$_.Exception.Message }
}

# 10) Print summary
$fail = $results | Where-Object { $_.status -eq "FAIL" }
$pass = $results | Where-Object { $_.status -eq "PASS" }

""
"=== PROJECT HEALTH CHECK ==="
$results | ForEach-Object { "{0,-22}  {1,-5}  {2}" -f $_.name, $_.status, $_.note }
""
"PASS: $($pass.Count)    FAIL: $($fail.Count)"
if ($fail.Count -gt 0) {
  "`nIssues detected. Quick fix tips:"
  foreach ($r in $fail) {
    switch -Wildcard ($r.name) {
      "Node *" { " - Upgrade Node to >=18 (use nvm-windows or official installer)." }
      "*.json:compilerOptions.*" { " - Re-run the tsconfig patch step or set baseUrl='.' and paths:{'@/*':['src/*']}." }
      "pkg:scripts.*" { " - Re-run the package.json scripts patch or add the missing script." }
      "*.gitignore" { " - Add a .gitignore with dist, node_modules, coverage, .env." }
      "eslint run" { " - Ensure eslint deps installed and .eslintrc.json is valid." }
      "build*" { " - Try 'npm run build' and read the error; often bad tsconfig or missing types." }
      "runtime smoke" { " - Check dist/main.js exports/imports and tsconfig module settings." }
      "coverage*" { " - Vitest installed? Try 'npm i -D vitest @vitest/coverage-v8'." }
      default { " - $($r.name): $($r.note)" }
    }
  }
}
