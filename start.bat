@echo off
chcp 65001 >nul
echo ========================================
echo   ZZZ AI Robot Startup Script
echo ========================================
echo.

cd /d D:\mySoft_code\ZZZAi

echo [1/2] Starting NoneBot2...
start "NoneBot2" cmd /k "cd /d D:\mySoft_code\ZZZAi && python bot.py"

timeout /t 3 /nobreak >nul

echo [2/2] Starting NapCat...
cd /d D:\mySoft_code\ZZZAi\napcat

set "QQPath=C:\Program Files\Tencent\QQNT\QQ.exe"
set NAPCAT_PATCH_PACKAGE=%cd%\qqnt.json
set NAPCAT_LOAD_PATH=%cd%\loadNapCat.js
set NAPCAT_INJECT_PATH=%cd%\NapCatWinBootHook.dll
set NAPCAT_LAUNCHER_PATH=%cd%\NapCatWinBootMain.exe
set NAPCAT_MAIN_PATH=%cd%\napcat.mjs

if not exist "%QQPath%" (
    echo [ERROR] QQ NT client not found
    echo Download: https://im.qq.com/pcqq/index.shtml
    pause
    exit /b
)

set NAPCAT_MAIN_PATH=%NAPCAT_MAIN_PATH:\=/%
echo (async () =^> {await import("file:///%NAPCAT_MAIN_PATH%")})() > "%NAPCAT_LOAD_PATH%"

echo Starting NapCat...
"%NAPCAT_LAUNCHER_PATH%" "%QQPath%" "%NAPCAT_INJECT_PATH%" %*

pause
