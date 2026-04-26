# Start Neo4j Server for Conference Management App

Write-Host "================================" -ForegroundColor Green
Write-Host "Starting Neo4j Database" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
cd $projectDir

# Set Java path to portable Java
$javaDir = "$projectDir\java"
if (Test-Path $javaDir) {
    $env:JAVA_HOME = $javaDir
    Write-Host "Using portable Java from: $javaDir" -ForegroundColor Cyan
} else {
    Write-Host "Warning: Portable Java not found in $javaDir" -ForegroundColor Yellow
}

# Set Neo4j home
$neo4jDir = "$projectDir\neo4j"
if (-not (Test-Path $neo4jDir)) {
    Write-Host "Error: Neo4j not found in $neo4jDir" -ForegroundColor Red
    exit 1
}

Write-Host "Neo4j directory: $neo4jDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Neo4j server..." -ForegroundColor Yellow
Write-Host ""

# Start Neo4j
$neo4jBin = "$neo4jDir\bin\neo4j.bat"

if (Test-Path $neo4jBin) {
    # Run Neo4j in foreground
    & $neo4jBin console
} else {
    Write-Host "Error: Neo4j startup script not found" -ForegroundColor Red
    exit 1
}
