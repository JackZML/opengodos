@echo off
echo ========================================
echo OpenGodOS 集成启动器
echo 启动Web应用 + 数字生命球体
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 步骤1: 检查依赖...
python -c "import tkinter; import requests; import psutil; print('依赖检查通过')" >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 缺少某些依赖，尝试安装...
    pip install requests psutil >nul 2>&1
)

echo 步骤2: 启动Web应用...
start /B cmd /c "cd /d %~dp0 && python run_web.py"
echo Web应用启动中，等待3秒...
timeout /t 3 /nobreak >nul

echo 步骤3: 验证Web应用...
curl -s -o nul -w "%%{http_code}" http://localhost:5000/api/data/health > web_status.txt
set /p WEB_STATUS=<web_status.txt
del web_status.txt

if "%WEB_STATUS%"=="200" (
    echo ✅ Web应用运行正常 (状态码: %WEB_STATUS%)
) else (
    echo ⚠️ Web应用可能未启动 (状态码: %WEB_STATUS%)
    echo 继续启动球体...
)

echo 步骤4: 启动数字生命球体...
echo 注意: 球体会出现在屏幕右下角
echo.
start /B cmd /c "cd /d %~dp0 && python digital_life_sphere.py"

echo.
echo ✅ 启动完成！
echo.
echo 系统状态:
echo   • Web界面: http://localhost:5000
echo   • 拓扑编辑器: http://localhost:5000/topology
echo   • 数据API: http://localhost:5000/api/data/dashboard
echo.
echo 球体操作:
echo   • 位置: 屏幕右下角
echo   • 左键点击: 展开交流界面
echo   • 右键点击: 显示功能菜单
echo   • 鼠标悬停: 增强发光效果
echo.
echo 按任意键查看详细状态...
pause >nul

echo.
echo 详细状态:
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE

echo.
echo 按任意键退出...
pause >nul