@echo off
echo ========================================
echo OpenGodOS v1.0.0 - Web应用启动器
echo ========================================
echo.

echo 启动OpenGodOS Web应用...
echo 访问: http://localhost:5000
echo.

REM 停止现有Web进程
taskkill /F /IM python.exe /FI "WINDOWTITLE eq OpenGodOS*" 2>nul
taskkill /F /IM python.exe /FI "COMMANDLINE eq *run_web.py*" 2>nul

REM 等待1秒
timeout /t 1 /nobreak >nul

REM 启动Web应用
cd /d %~dp0
start "OpenGodOS Web" python run_web.py

echo.
echo ✅ Web应用已启动！
echo 📍 访问地址: http://localhost:5000
echo.
echo 功能:
echo   1. 主界面 - 系统状态概览
echo   2. 拓扑编辑器 - http://localhost:5000/topology
echo   3. 数据API - http://localhost:5000/api/data/dashboard
echo.
echo 按任意键退出...
pause >nul