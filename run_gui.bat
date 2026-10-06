@echo off
setlocal
chcp 65001 > nul
title 本地 AI 视频字幕翻译与封装工作台 (Local Subtitler Pro)

cd /d "%~dp0"

set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [错误] 未找到 Python 虚拟环境: "%PYTHON_EXE%"
    echo 请确认环境安装完整。
    pause
    exit /b 1
)

echo -----------------------------------------------------------
echo 正在启动 本地 AI 视频字幕翻译与封装工作台...
echo 如遇问题，此窗口将保留错误日志以供排查。
echo -----------------------------------------------------------

"%PYTHON_EXE%" gui_app.py

if errorlevel 1 (
    echo.
    echo ===========================================================
    echo [提示] 应用程序异常退出（退出代码: %errorlevel%）。
    echo 请查看上方报错信息，或查看 gui_crash.log 日志。
    echo ===========================================================
    pause
)

endlocal
