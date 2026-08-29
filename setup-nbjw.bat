@echo off
setlocal EnableExtensions

rem Touchline -- Windows setup for auto calibration (No Bells, Just Whistles).
rem Clones the NBJW repo and downloads the SV_kp / SV_lines weights.
rem Requires Git for Windows (https://git-scm.com/download/win).

cd /d "%~dp0"

set "THIRD_PARTY=third_party"
set "NBJW=%THIRD_PARTY%\no-bells-just-whistles"
set "NBJW_KP_URL=https://github.com/mguti97/No-Bells-Just-Whistles/releases/download/v1.0.0/SV_kp"
set "NBJW_LINES_URL=https://github.com/mguti97/No-Bells-Just-Whistles/releases/download/v1.0.0/SV_lines"

echo.
echo  Touchline -- auto calibration setup (NBJW)
echo  ------------------------------------------

where git >nul 2>nul
if errorlevel 1 (
    echo.
    echo  ERROR: git was not found.
    echo  Install Git for Windows from https://git-scm.com/download/win
    echo  and try again.
    echo.
    pause
    exit /b 1
)

if not exist "%NBJW%\inference.py" (
    echo.
    echo  Cloning No Bells, Just Whistles...
    if not exist "%THIRD_PARTY%" mkdir "%THIRD_PARTY%"
    git clone --depth 1 https://github.com/mguti97/no-bells-just-whistles "%NBJW%"
    if errorlevel 1 goto :fail
)

if not exist "%NBJW%\SV_kp" (
    echo.
    echo  Downloading SV_kp weights...
    curl -fL -o "%NBJW%\SV_kp" "%NBJW_KP_URL%"
    if errorlevel 1 goto :fail
)

if not exist "%NBJW%\SV_lines" (
    echo.
    echo  Downloading SV_lines weights...
    curl -fL -o "%NBJW%\SV_lines" "%NBJW_LINES_URL%"
    if errorlevel 1 goto :fail
)

echo.
echo  Auto calibration ready. Run:
echo    run.bat path\to\match.mp4 --auto-calibrate third_party\no-bells-just-whistles
echo.
pause
exit /b 0

:fail
echo.
echo  Setup failed. See the messages above.
echo.
pause
exit /b 1
