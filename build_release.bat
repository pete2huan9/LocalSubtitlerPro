@echo off
setlocal
chcp 65001 > nul
title Local Subtitler Pro (v0.2.0) - 一键打包发布脚本

cd /d "%~dp0"

set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [错误] 未找到项目虚拟环境: %PYTHON_EXE%
    pause
    exit /b 1
)

echo ============================================================
echo   Local Subtitler Pro (v0.2.0) 一键 EXE 打包构建工具
echo ============================================================
echo.

"%PYTHON_EXE%" build_exe.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败，请检查上方日志。
    pause
    exit /b 1
)

echo.
echo 构建成功！成果位于 dist/ 目录下。
echo.
pause
endlocal
