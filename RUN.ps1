# Simple Startup - Just Run This!

Write-Host "================================" -ForegroundColor Green
Write-Host "Conference Management App" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "SQLite (No server needed) + Neo4j (Graph)" -ForegroundColor Cyan
Write-Host ""

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
cd $projectDir

# Check if database exists, if not create it
if (-not (Test-Path "appdbproj.db")) {
    Write-Host "Creating SQLite database with sample data..." -ForegroundColor Yellow
    .\venv\Scripts\python.exe import_sqlite_data.py
    Write-Host ""
}

# Try to import Neo4j data if Neo4j is running
Write-Host "Checking Neo4j connection..." -ForegroundColor Cyan
$testConnection = Test-NetConnection -ComputerName localhost -Port 7687 -WarningAction SilentlyContinue
if ($testConnection.TcpTestSucceeded) {
    Write-Host "Neo4j is running! Importing graph data..." -ForegroundColor Green
    .\venv\Scripts\python.exe import_neo4j_data.py
} else {
    Write-Host "Neo4j not running - graph features disabled" -ForegroundColor Yellow
    Write-Host "To enable Options 4 & 5, start Neo4j: .\START-NEO4J.ps1" -ForegroundColor Yellow
}
Write-Host ""

# Activate virtual environment
Write-Host "Starting application..." -ForegroundColor Cyan
Write-Host ""

& .\venv\Scripts\Activate.ps1
python main.py
