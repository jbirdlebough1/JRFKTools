@echo off
title JRFK Migrator & Station Workbench Launcher
echo =========================================================================
echo  JRFK 32-to-64 Bit Appliance Migrator & Station Workbench Launcher
echo  RF-KIT RF2K+ / RF2K-S Solid-State Linear Power Amplifiers
echo =========================================================================
echo.

cd /d "%~dp0"

:: Check for Administrator elevation (required on Windows 11 for raw SD card operations)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Elevating to Administrator via Windows UAC...
    wscript.exe "%~dp0tools\migrator\elevate.vbs"
    exit /b
)

echo [*] Checking Python 3 runtime...
set "PYTHON_EXE=python"
python --version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Program Files\CLE\python_runtime\python.exe" (
        set "PYTHON_EXE=C:\Program Files\CLE\python_runtime\python.exe"
    ) else (
        echo [ERROR] Python is not found in PATH!
        echo Please install Python 3.10+ from python.org or the Microsoft Store.
        pause
        exit /b 1
    )
)

echo [+] Python detected: %PYTHON_EXE%
echo [*] Freeing port 8089 if in use...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8089" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1

echo [*] Launching JRFK Migrator Web Service on http://127.0.0.1:8089...
start "" http://127.0.0.1:8089/JRFK_32_to_64Bit_Migration_tool.htm

"%PYTHON_EXE%" tools\migrator\server.py 8089
pause
