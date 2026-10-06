@echo off
setlocal
title AKB48 Subtitle Generator (AMD 8845HS)

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"
set "MAIN_PY=%SCRIPT_DIR%video_subtitler.py"

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python environment not found in venv.
    pause
    exit /b 1
)

set "INPUT_FILE=%~1"

if "%INPUT_FILE%"=="" (
    echo ======================================================================
    echo   AKB48 Video Subtitle Tool (AMD 8845HS + DDR5-5600)
    echo ======================================================================
    echo Please drag and drop your video file into this window and press ENTER:
    set /p "INPUT_FILE=Video Path: "
)

:: Strip surrounding quotes
set "INPUT_FILE=%INPUT_FILE:"=%"

if not exist "%INPUT_FILE%" (
    echo [ERROR] File not found: "%INPUT_FILE%"
    pause
    exit /b 1
)

echo.
echo Processing video: "%INPUT_FILE%"
echo Starting AI pipeline...
echo.

"%PYTHON_EXE%" "%MAIN_PY%" --video "%INPUT_FILE%"

echo.
echo ======================================================================
echo Done! Subtitled MKV and SRT have been saved to your video directory.
echo ======================================================================
pause
