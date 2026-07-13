# PowerShell \u4e00\u952e\u90e8\u7f72\u5165\u53e3(Windows \u7528\u6237\u7528)
# \u7528\u6cd5: PS D:\douban-bigdata> .\scripts\deploy.ps1

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

# 1) DATA_ROOT \u9ed8\u8ba4 D:\douban-bigdata,\u7528\u6237\u53ef\u901a\u8fc7 $env:DATA_ROOT \u8986\u76d6
if (-not $env:DATA_ROOT) { $env:DATA_ROOT = "D:/douban-bigdata" }
Write-Host ">>> DATA_ROOT = $env:DATA_ROOT"

$dataDirs = @("mysql-data", "data\raw", "logs\backend", "dist")
foreach ($sub in $dataDirs) {
    $path = Join-Path $env:DATA_ROOT $sub
    if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path -Force | Out-Null }
}

# 2) \u51c6\u5907\u79cd\u5b50\u6570\u636e(\u82e5\u7528\u6237\u8dd1\u8fc7 ETL \u5219\u5df2\u5b58\u5728)
$seedDir = Join-Path $repoRoot "scripts\seed-data"
$schemaSql = Join-Path $seedDir "01-schema.sql"
if (-not (Test-Path $schemaSql)) {
    Write-Host ">>> generate seed data"
    & python scripts\generate_seed_data.py
}

# 3) \u524d\u7aef\u6784\u5efa
$distPath = Join-Path $env:DATA_ROOT "dist"
if (-not (Test-Path $distPath) -or -not (Get-ChildItem $distPath -ErrorAction SilentlyContinue)) {
    Write-Host ">>> build frontend"
    Push-Location frontend
    if (-not (Test-Path node_modules)) { npm install }
    npm run build
    Copy-Item -Path "dist\*" -Destination $distPath -Recurse -Force
    Pop-Location
}

# 4) \u542f\u52a8
Write-Host ">>> docker compose up -d --build"
$composeCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $composeCmd) { throw "docker not installed. Install Docker Desktop first." }
& docker compose --env-file .env up -d --build

# 5) \u5065\u5eb7\u68c0\u67e5(\u8d70 nginx \u53cd\u4ee3,backend \u5bb9\u5668\u4ec5\u5728 douban-net \u5185\u7f51\u53ef\u8bbf\u95ee)
Write-Host ">>> health check"
$nginxPort = $env:NGINX_HOST_PORT
if (-not $nginxPort) {
    $line = Get-Content .env | Select-String -Pattern '^NGINX_HOST_PORT=' | Select-Object -First 1
    if ($line) { $nginxPort = ($line -split '=',2)[1].Trim() }
}
if (-not $nginxPort) { $nginxPort = "8080" }
$healthUrl = "http://127.0.0.1:${nginxPort}/api/health"
Start-Sleep -Seconds 10
for ($i = 1; $i -le 5; $i++) {
    try {
        $r = Invoke-WebRequest -Uri $healthUrl -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200) { Write-Host "    [OK] backend health passed via $healthUrl"; break }
    } catch {}
    Write-Host "    retry $i/5 ($healthUrl)"
    Start-Sleep -Seconds 3
}

Write-Host ">>> done"
Write-Host "    frontend: http://127.0.0.1:${nginxPort}"
Write-Host "    backend:  http://127.0.0.1:5000 (\u5185\u7f51,\u4e0d\u66b4\u9732\u5bbf\u4e3b)"
Write-Host "    mysql:    127.0.0.1:3306 (user=douban, db=douban)"
Write-Host "    data:     $env:DATA_ROOT"
