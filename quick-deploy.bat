@echo off
echo ========================================
echo Course Extractor Quick Deploy
echo ========================================
echo.

echo This script will deploy your Course Extractor to GitHub and Heroku automatically.
echo.

echo Step 1: Checking Git status...
git status

echo.
echo Step 2: Adding all files...
git add .

echo.
echo Step 3: Committing changes...
git commit -m "Auto-deploy: $(date /t) $(time /t)"

echo.
echo Step 4: Checking if remote origin exists...
git remote -v | findstr origin >nul
if %errorlevel% neq 0 (
    echo ERROR: No remote origin found!
    echo Please run setup-git.bat first to set up your GitHub repository.
    pause
    exit /b 1
)

echo.
echo Step 5: Pushing to GitHub...
git push origin main

echo.
echo Step 6: Checking if Heroku remote exists...
git remote -v | findstr heroku >nul
if %errorlevel% neq 0 (
    echo WARNING: No Heroku remote found!
    echo Please create a Heroku app first:
    echo   heroku create your-app-name
    echo   git remote add heroku https://git.heroku.com/your-app-name.git
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo.
echo Step 7: Deploying to Heroku...
git push heroku main

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Your Course Extractor is now:
echo - ✅ Pushed to GitHub
echo - ✅ Deployed to Heroku
echo - ✅ Publicly accessible!
echo.
echo Run 'heroku open' to view your live app.
echo.
pause
