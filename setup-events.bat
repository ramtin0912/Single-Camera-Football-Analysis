@echo off
setlocal EnableExtensions

rem Touchline -- Windows setup for events (ball-action-spotting).
rem Clones the action-spotting repo. The model weights live on Google Drive
rem and must be downloaded by hand (see the messages below).
rem Requires Git for Windows (https://git-scm.com/download/win).

cd /d "%~dp0"

set "THIRD_PARTY=third_party"
set "ACTION=%THIRD_PARTY%\ball-action-spotting"

echo.
echo  Touchline -- events setup (ball-action-spotting)
echo  ------------------------------------------------

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

if not exist "%ACTION%\src\predictors.py" (
    echo.
    echo  Cloning ball-action-spotting...
    if not exist "%THIRD_PARTY%" mkdir "%THIRD_PARTY%"
    git clone --depth 1 https://github.com/lRomul/ball-action-spotting "%ACTION%"
    if errorlevel 1 goto :fail
)

echo.
echo  Action-spotting repo cloned into %ACTION%.
echo.
echo  Remaining manual steps (the weights live on Google Drive):
echo    1. Open the "Trained models" link in %ACTION%\README.md
echo    2. Unpack it so this folder exists:
echo       %ACTION%\data\ball_action\experiments\sampling_weights_001\
echo    3. Follow the Docker steps in README.md section 3 (needs an NVIDIA GPU;
echo       on Windows, Docker runs inside WSL2).
echo.
pause
exit /b 0

:fail
echo.
echo  Setup failed. See the messages above.
echo.
pause
exit /b 1
