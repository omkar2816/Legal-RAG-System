# PowerShell script to build and run the Legal RAG System Docker container

$ErrorActionPreference = "Stop"

Write-Host "=== Legal RAG System Docker Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path -Path ".env")) {
    Write-Host "⚠️ .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item -Path "env_template.txt" -Destination ".env"
    Write-Host "⚠️ Please edit the .env file to add your API keys before continuing." -ForegroundColor Yellow
    Write-Host "Press Enter to continue or Ctrl+C to abort..." -ForegroundColor Yellow
    Read-Host
}

# Check if Docker is installed
try {
    docker --version | Out-Null
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    $useCompose = $true
} catch {
    $useCompose = $false
}

if ($useCompose) {
    Write-Host "🐳 Using Docker Compose for deployment" -ForegroundColor Green
    Write-Host "Building and starting containers..." -ForegroundColor Green
    docker-compose up --build -d
    
    Write-Host ""
    Write-Host "✅ Legal RAG System is now running!" -ForegroundColor Green
    Write-Host "📝 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "🔍 Health Check: http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To initialize the Pinecone index, run:" -ForegroundColor Yellow
    Write-Host "docker-compose exec legal-rag-app python create_pinecone_index.py" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Yellow
    Write-Host "docker-compose logs -f" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To stop the application:" -ForegroundColor Yellow
    Write-Host "docker-compose down" -ForegroundColor Yellow
    
} else {
    Write-Host "🐳 Using Docker for deployment (Docker Compose not found)" -ForegroundColor Green
    Write-Host "Building Docker image..." -ForegroundColor Green
    docker build -t legal-rag-system -f docker.dockerfile .
    
    Write-Host "Creating necessary directories..." -ForegroundColor Green
    if (-not (Test-Path -Path "uploads")) { New-Item -Path "uploads" -ItemType Directory | Out-Null }
    if (-not (Test-Path -Path "processed")) { New-Item -Path "processed" -ItemType Directory | Out-Null }
    if (-not (Test-Path -Path "logs")) { New-Item -Path "logs" -ItemType Directory | Out-Null }
    
    Write-Host "Starting container..." -ForegroundColor Green
    $currentDir = (Get-Location).Path
    
    docker run -d --name legal-rag-system `
        -p 8000:8000 `
        -v "${currentDir}\uploads:/app/uploads" `
        -v "${currentDir}\processed:/app/processed" `
        -v "${currentDir}\logs:/app/logs" `
        --env-file .env `
        legal-rag-system
    
    Write-Host ""
    Write-Host "✅ Legal RAG System is now running!" -ForegroundColor Green
    Write-Host "📝 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "🔍 Health Check: http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To initialize the Pinecone index, run:" -ForegroundColor Yellow
    Write-Host "docker exec -it legal-rag-system python create_pinecone_index.py" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Yellow
    Write-Host "docker logs -f legal-rag-system" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To stop the application:" -ForegroundColor Yellow
    Write-Host "docker stop legal-rag-system; docker rm legal-rag-system" -ForegroundColor Yellow
}