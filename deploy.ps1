# Course Extractor Deployment Script
Write-Host "========================================" -ForegroundColor Green
Write-Host "Course Extractor Deployment Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Step 1: Checking Git status..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "Step 2: Adding all files..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "Step 3: Committing changes..." -ForegroundColor Yellow
git commit -m "Deploy to production"

Write-Host ""
Write-Host "Step 4: Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "Step 5: Deploying to Heroku..." -ForegroundColor Yellow
git push heroku main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your app should now be live on Heroku!" -ForegroundColor Cyan
Write-Host "Run 'heroku open' to view it in your browser." -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue"
