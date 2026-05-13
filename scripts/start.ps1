# Start script for Windows PowerShell

Write-Host "Starting Project Management MVP..." -ForegroundColor Green
docker-compose up --build -d

Write-Host ""
Write-Host "Application starting..." -ForegroundColor Cyan
Write-Host "Visit http://localhost:8000 when ready" -ForegroundColor Yellow
Write-Host ""
Write-Host "To view logs: docker-compose logs -f" -ForegroundColor Gray
Write-Host "To stop: .\scripts\stop.ps1" -ForegroundColor Gray

# Made with Bob
