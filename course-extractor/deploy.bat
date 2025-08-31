@echo off
echo ========================================
echo Course Extractor Deployment Script
echo ========================================
echo.

echo Step 1: Checking Git status...
git status

echo.
echo Step 2: Adding all files...
git add .

echo.
echo Step 3: Committing changes...
git commit -m "Deploy to production"

echo.
echo Step 4: Pushing to GitHub...
git push origin main

echo.
echo Step 5: Deploying to Heroku...
git push heroku main

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Your app should now be live on Heroku!
echo Run 'heroku open' to view it in your browser.
echo.
pause
