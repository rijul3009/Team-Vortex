@echo off
title Intelligent Expense & Budget Monitoring System Launcher
echo =====================================================================
echo    INTELLIGENT EXPENSE AND BUDGET MONITORING SYSTEM
echo =====================================================================
echo.
echo Starting Backend API Server (Port 5000)...
start "Finance Backend (Port 5000)" cmd /k "cd /d %~dp0server && npm.cmd run dev"

echo Starting Frontend UI Server (Port 5173)...
start "Finance Frontend (Port 5173)" cmd /k "cd /d %~dp0client && npm.cmd run dev"

echo.
echo =====================================================================
echo  Both servers have been launched in separate windows!
echo  
echo  Frontend URL : http://localhost:5173
echo  Backend API  : http://localhost:5000
echo  Health Check : http://localhost:5000/health
echo  
echo  Demo Credentials:
echo    Email:    demo@financial.com
echo    Password: Password123!
echo    (Or click "1-Click Demo Sign In" on the login screen)
echo =====================================================================
echo.
timeout /t 5 >nul
start http://localhost:5173
