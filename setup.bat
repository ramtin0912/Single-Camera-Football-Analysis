@echo off
setlocal EnableExtensions

rem Touchline -- Windows setup (double-click, or run from cmd).
rem Creates .venv, installs dependencies, and pre-downloads the YOLOv8n weights.
rem Requires Python 3.10+ (https://www.python.org/downloads/).
rem When called by run.bat / smoke-test.bat, TOUCHLINE_NOPAUSE is set so the
rem final "press any key" prompt is skipped and control returns to the caller.

cd /d "%~dp0"

echo.
echo  Touchline setup (Windows)
echo  -------------------------

rem --- Find a Python 3.10+ interpreter: prefer the `py` launcher, then `python`.
set "PY=py"
py -3 --version >nul 2>nul
if errorlevel 1 (
    set "PY=python"
    python --version >nul 2>nul
    if errorlevel 1 goto :nopython
)

echo  Using interpreter: %PY%
%PY% --version

rem --- Create the virtual environment if it doesn't exist yet.
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo  Creating virtual environment .venv ...
    %PY% -m venv .venv
    if errorlevel 1 goto :fail
) else (
    echo.
    echo  Virtual environment already present at .venv
)

rem --- Install dependencies.
echo.
echo  Installing dependencies (this can take several minutes)...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :fail
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

rem --- Pre-download the YOLOv8n weights (cached for the first run).
echo.
echo  Pre-downloading YOLOv8 weights...
".venv\Scripts\python.exe" -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
if errorlevel 1 goto :fail

echo.
echo  Setup complete. Next step:
echo    run.bat path\to\match.mp4
echo  (or drag a video file onto run.bat)
echo.
if defined TOUCHLINE_NOPAUSE exit /b 0
pause
exit /b 0

:nopython
echo.
echo  ERROR: Python 3.10+ was not found.
echo  Install it from https://www.python.org/downloads/
echo  and tick "Add Python to PATH" during install.
echo.
pause
exit /b 1

:fail
echo.
echo  Setup failed. See the messages above.
echo.
pause
exit /b 1
