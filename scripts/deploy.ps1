# PowerShell 一键部署入口(Windows 用户用)
# 用法: PS D:\douban-bigdata> .\scripts\deploy.ps1

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

# 1) DATA_ROOT 默认 D:\douban-bigdata,用户可通过 $env:DATA_ROOT 覆盖
if (-not $env:DATA_ROOT) { $env:DATA_ROOT = "D:/douban-bigdata" }
Write-Host ">>> DATA_ROOT = $env:DATA_ROOT"

$dataDirs = @("mysql-data", "data\raw", "logs\backend", "dist")
foreach ($sub in $dataDirs) {
    $path = Join-Path $env:DATA_ROOT $sub
    if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path -Force | Out-Null }
}

# 2) 准备种子数据
$seedDir = Join-Path $repoRoot "scripts\seed-data"
$schemaSql = Join-Path $seedDir "01-schema.sql"
if (-not (Test-Path $schemaSql)) {
    Write-Host ">>> generate seed data"
    & .\.venv\Scripts\python.exe scripts\generate_seed_data.py
}

# 3) 前端构建
$distPath = Join-Path $env:DATA_ROOT "dist"
if (-not (Test-Path $distPath) -or -not (Get-ChildItem $distPath -ErrorAction SilentlyContinue)) {
    Write-Host ">>> build frontend"
    Push-Location frontend
    if (-not (Test-Path node_modules)) { npm install }
    npm run build
    Copy-Item -Path "dist\*" -Destination $distPath -Recurse -Force
    Pop-Location
}

# 4) 启动
Write-Host ">>> docker compose up -d --build"
$composeCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $composeCmd) { throw "docker not installed. Install Docker Desktop first." }
& docker compose --env-file .env up -d --build

# 5) 健康检查
Write-Host ">>> health check"
Start-Sleep -Seconds 10
for ($i = 1; $i -le 5; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200) { Write-Host "    [OK] backend health passed"; break }
    } catch {}
    Write-Host "    retry $i/5"
    Start-Sleep -Seconds 3
}

Write-Host ">>> done"
Write-Host "    frontend: http://127.0.0.1:8080"
Write-Host "    backend:  http://127.0.0.1:5000"
Write-Host "    mysql:    127.0.0.1:3306 (user=douban, db=douban)"
Write-Host "    data:     $env:DATA_ROOT"