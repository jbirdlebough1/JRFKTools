@echo off
title JRFK Migrator & Station Workbench Launcher
echo =========================================================================
echo  JRFK 32-to-64 Bit Appliance Migrator & Station Workbench Launcher
echo  RF-KIT RF2K+ / RF2K-S Solid-State Linear Power Amplifiers
echo =========================================================================
echo.

cd /d "%~dp0"

:: Single UAC elevation prompt at startup (inherited by RPi Imager & disk tools)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Requesting Administrator elevation via Windows UAC...
    wscript.exe "%~dp0tools\migrator\elevate.vbs"
    exit /b
)

echo [*] Checking Python 3 runtime...
set "PYTHON_EXE="
if exist "%~dp0tools\python\python.exe" (
    set "PYTHON_EXE=%~dp0tools\python\python.exe"
) else (
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=python"
    ) else if exist "C:\Program Files\CLE\python_runtime\python.exe" (
        set "PYTHON_EXE=C:\Program Files\CLE\python_runtime\python.exe"
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python 3.10+ not found in tools\python\, PATH, or CLE python_runtime!
    pause
    exit /b 1
)

echo [+] Python detected: %PYTHON_EXE%
echo [*] Stopping any stale JRFK server on port 8089...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8089" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1

echo [*] Starting JRFK Migrator Web Service on http://127.0.0.1:8089...
start "JRFK Migrator Server" /MIN "%PYTHON_EXE%" "%~dp0tools\migrator\server.py" 8089

:: Wait cleanly until port 8089 responds before opening browser
powershell -NoProfile -NonInteractive -Command "for($i=0;$i -lt 30;$i++){ try{ $c=New-Object Net.Sockets.TcpClient('127.0.0.1',8089); $c.Close(); exit 0 } catch { Start-Sleep -Milliseconds 300 } }" >nul 2>&1

echo [+] Server online. Opening JRFK Migrator UI in your browser...
start "" "http://127.0.0.1:8089/JRFK_32_to_64Bit_Migration_tool.htm"
echo [*] Keep the minimized 'JRFK Migrator Server' window open while migrating.
