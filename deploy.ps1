# Deployment script for Room Reservation System (Windows PowerShell)
# Usage: .\deploy.ps1 [dev|prod]

param(
    [string]$Env = "dev"
)

Write-Host "🚀 Starting deployment for environment: $Env" -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ docker-compose is not installed. Please install it and try again." -ForegroundColor Red
    exit 1
}

# Create .env files if they don't exist
if (-not (Test-Path "backend\.env")) {
    Write-Host "📝 Creating backend\.env from example..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "⚠️  Please edit backend\.env with your MongoDB connection string" -ForegroundColor Yellow
}

if (-not (Test-Path "frontend\.env")) {
    Write-Host "📝 Creating frontend\.env from example..." -ForegroundColor Yellow
    Copy-Item "frontend\.env.example" "frontend\.env"
    Write-Host "⚠️  Please edit frontend\.env with your backend URL" -ForegroundColor Yellow
}

# Build and start services
Write-Host "🔨 Building and starting services..." -ForegroundColor Cyan
docker-compose down
docker-compose build
docker-compose up -d

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "📊 Service status:" -ForegroundColor Cyan
docker-compose ps

# Show logs
Write-Host ""
Write-Host "📋 Recent logs:" -ForegroundColor Cyan
docker-compose logs --tail=20

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "🔌 Backend API: http://localhost:8001" -ForegroundColor Green
Write-Host "📚 API Docs: http://localhost:8001/docs" -ForegroundColor Green
Write-Host ""
Write-Host "To view logs: docker-compose logs -f" -ForegroundColor Cyan
Write-Host "To stop: docker-compose down" -ForegroundColor Cyan
