@echo off
echo ========================================
echo Deploying to Railway
echo ========================================
echo.

echo Checking Railway CLI...
railway --version >nul 2>&1
if errorlevel 1 (
    echo Railway CLI not found!
    echo Install it with: npm i -g @railway/cli
    pause
    exit /b 1
)

echo.
echo Adding changes to git...
git add .

echo.
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Deploy backend updates

echo.
echo Committing changes...
git commit -m "%commit_msg%"

echo.
echo Pushing to Railway...
railway up

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Backend URL: https://max-backend-production.up.railway.app
echo Frontend URL: https://realwin-frontend-master.vercel.app
echo.
echo Checking deployment logs...
railway logs --limit 50

echo.
pause
