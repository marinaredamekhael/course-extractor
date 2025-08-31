# Course Extractor Git Setup Script
Write-Host "========================================" -ForegroundColor Green
Write-Host "Course Extractor Git Setup Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "This script will help you set up Git and push to GitHub." -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Checking if Git is installed..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host $gitVersion -ForegroundColor Green
} catch {
    Write-Host "ERROR: Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/" -ForegroundColor Red
    Write-Host "Then run this script again." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""
Write-Host "Step 2: Checking Git configuration..." -ForegroundColor Yellow
Write-Host "Current Git user:" -ForegroundColor Cyan
git config --global user.name
Write-Host "Current Git email:" -ForegroundColor Cyan
git config --global user.email

Write-Host ""
Write-Host "Step 3: Setting up Git repository..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Cyan
    git init
    Write-Host "Adding all files..." -ForegroundColor Cyan
    git add .
    Write-Host "Making initial commit..." -ForegroundColor Cyan
    git commit -m "Initial commit: Course Extractor Flask app"
    Write-Host "Git repository initialized successfully!" -ForegroundColor Green
} else {
    Write-Host "Git repository already exists." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "NEXT STEPS:" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. Go to GitHub.com and create a new repository" -ForegroundColor Cyan
Write-Host "2. Name it: course-extractor" -ForegroundColor Cyan
Write-Host "3. Make it PUBLIC" -ForegroundColor Cyan
Write-Host "4. Don't initialize with README (we already have one)" -ForegroundColor Cyan
Write-Host "5. Copy the repository URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "6. Then run these commands:" -ForegroundColor Yellow
Write-Host "   git remote add origin YOUR_REPOSITORY_URL" -ForegroundColor White
Write-Host "   git branch -M main" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "7. Finally, deploy to Heroku:" -ForegroundColor Yellow
Write-Host "   heroku create your-app-name" -ForegroundColor White
Write-Host "   git push heroku main" -ForegroundColor White
Write-Host ""
Write-Host "See DEPLOYMENT.md for detailed instructions!" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to continue"
