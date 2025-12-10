@echo off
echo 正在启动刷题系统...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未检测到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 安装依赖
echo 正在检查并安装依赖...
pip install -r requirements.txt

REM 启动应用
echo.
echo 启动刷题系统...
python quiz_app.py

pause