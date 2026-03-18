@echo off
echo ========================================
echo OpenGodOS 完整启动器
echo 同时启动Web应用和数字生命球体
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 步骤1: 启动Web应用...
start /B python run_web.py
timeout /t 3 /nobreak >nul

echo 步骤2: 启动数字生命球体...
start /B python digital_life_sphere.py
timeout /t 2 /nobreak >nul

echo.
echo ✅ 启动完成！
echo.
echo 访问地址:
echo   • Web界面: http://localhost:5000
echo   • 拓扑编辑器: http://localhost:5000/topology
echo   • 数据API: http://localhost:5000/api/data/dashboard
echo.
echo 球体操作:
echo   • 位置: 屏幕右下角
echo   • 左键点击: 展开交流界面
echo   • 右键点击: 显示功能菜单
echo.
echo 按任意键查看状态...
pause >nul

echo.
echo 当前进程状态:
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE

echo.
echo 按任意键退出状态查看...
pause >nul