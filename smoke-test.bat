@echo off
setlocal EnableExtensions

rem Touchline -- Windows smoke test (double-click).
rem Verifies the metric core without a video or model. Expect 5 PASS.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo  Virtual environment not found - running setup first...
    echo.
    set "TOUCHLINE_NOPAUSE=1"
    call "%~dp0setup.bat"
    if errorlevel 1 exit /b 1
)

".venv\Scripts\python.exe" scripts\smoke_test.py
set "TEST_RESULT=%errorlevel%"

echo.
echo  Smoke test finished. See the PASS/FAIL results above.
echo.
pause
exit /b %TEST_RESULT%
