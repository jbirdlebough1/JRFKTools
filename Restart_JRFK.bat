@echo off
setlocal
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges to restart JRFK...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo [*] Stopping any running JRFK.exe, stalled rpi-imager, and JRFK Migrator server processes...
taskkill /F /IM JRFK.exe /T >nul 2>&1
taskkill /F /IM rpi-imager.exe /T >nul 2>&1
powershell -NoProfile -NonInteractive -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'tools\\migrator\\server\.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }; Get-NetTCPConnection -LocalPort 8089 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

timeout /t 1 /nobreak >nul
cd /d "D:\JRFK"
if exist "C:\Program Files\CLE\python_runtime\python.exe" (
    echo [*] Rebuilding D:\JRFK\JRFK.exe with latest fixes...
    "C:\Program Files\CLE\python_runtime\python.exe" "D:\JRFK\tools\migrator\build_jrfk_exe.py"
)

echo [+] Starting fresh JRFK.exe...
start "" "D:\JRFK\JRFK.exe"
endlocal
