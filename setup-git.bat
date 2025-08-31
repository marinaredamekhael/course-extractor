@echo off
echo ========================================
echo Course Extractor Git Setup Script
echo ========================================
echo.

echo This script will help you set up Git and push to GitHub.
echo.

echo Step 1: Checking if Git is installed...
git --version
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/
    echo Then run this script again.
    pause
    exit /b 1
)

echo.
echo Step 2: Checking Git configuration...
echo Current Git user:
git config --global user.name
echo Current Git email:
git config --global user.email

echo.
echo Step 3: Setting up Git repository...
if not exist .git (
    echo Initializing Git repository...
    git init
    echo Adding all files...
    git add .
    echo Making initial commit...
    git commit -m "Initial commit: Course Extractor Flask app"
    echo Git repository initialized successfully!
) else (
    echo Git repository already exists.
)

echo.
echo ========================================
echo NEXT STEPS:
echo ========================================
echo.
echo 1. Go to GitHub.com and create a new repository
echo 2. Name it: course-extractor
echo 3. Make it PUBLIC
echo 4. Don't initialize with README (we already have one)
echo 5. Copy the repository URL
echo.
echo 6. Then run these commands:
echo    git remote add origin YOUR_REPOSITORY_URL
echo    git branch -M main
echo    git push -u origin main
echo.
echo 7. Finally, deploy to Heroku:
echo    heroku create your-app-name
echo    git push heroku main
echo.
echo See DEPLOYMENT.md for detailed instructions!
echo.
pause
