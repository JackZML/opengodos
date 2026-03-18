@echo off
echo ========================================
echo 数字生命球体调试启动器
echo ========================================
echo.

REM 停止现有的球体进程
taskkill /F /IM python.exe /FI "WINDOWTITLE eq OpenGodOS*" 2>nul
echo 已停止现有球体进程

REM 等待1秒
timeout /t 1 /nobreak >nul

REM 启动球体并显示窗口
echo 启动数字生命球体...
echo 注意: 球体会出现在屏幕右下角
echo.

cd /d %~dp0
start "OpenGodOS Digital Life Sphere" python digital_life_sphere.py

echo.
echo 球体已启动！
echo.
echo 如果球体仍未显示，请尝试:
echo 1. 按 Alt+Tab 查看是否有"OpenGodOS"窗口
echo 2. 检查任务栏是否有Python窗口
echo 3. 尝试移动其他窗口，球体可能在后面
echo.
echo 按任意键退出...
pause >nul