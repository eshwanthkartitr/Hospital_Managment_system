# Clean up existing containers and volumes
Write-Host "Cleaning up existing containers..." -ForegroundColor Yellow
docker-compose down -v
docker system prune -f

# Create necessary directories
Write-Host "Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "./static"
New-Item -ItemType Directory -Force -Path "./templates"
New-Item -ItemType Directory -Force -Path "./uploads"

# Start the application
Write-Host "Starting application..." -ForegroundColor Green
docker-compose up --build -d

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
$attempts = 0
do {
    $attempts++
    $health = docker ps --format "{{.Names}}: {{.Status}}"
    Write-Host $health
    Start-Sleep -Seconds 2
} while ($health -match "starting" -and $attempts -lt 30)

# Show logs
Write-Host "Application is ready! Showing logs..." -ForegroundColor Green
docker-compose logs -f