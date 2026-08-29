@echo off
setlocal EnableExtensions

rem Touchline -- Windows run (double-click and drag a video onto it, or:
rem   run.bat "C:\path\to\match.mp4" [extra touchline options])
rem Runs the analysis pipeline. Creates the venv first if needed.

cd /d "%~dp0"

if "%~1"=="" (
    echo.
    echo  Usage: run.bat path\to\match.mp4 [extra options]
    echo.
    echo  Tip: drag a video file onto run.bat to run it.
    echo  Options: --out DIR, --frame-step N, --model NAME, --calibration FILE,
    echo          --auto-calibrate DIR, --include-events, ...  (see README.md)
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo  Virtual environment not found - running setup first...
    echo.
    set "TOUCHLINE_NOPAUSE=1"
    call "%~dp0setup.bat"
    if errorlevel 1 exit /b 1
)

".venv\Scripts\python.exe" -m touchline %*
if errorlevel 1 (
    echo.
    echo  The pipeline exited with an error. See the messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo  Done. Results are in the output\ folder (report.html, report.json, heatmaps).
echo.
pause
exit /b 0
