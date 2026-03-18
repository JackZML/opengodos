@echo off
echo ========================================
echo OpenGodOS 数字生命球体启动器
echo 基于《湮灭》概念的科幻启动器
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 正在启动数字生命球体...
echo 注意: 球体会出现在屏幕右下角
echo.

REM 启动球体
python digital_life_sphere.py

if %errorlevel% equ 0 (
    echo.
    echo 数字生命球体已启动！
    echo 操作说明:
    echo   • 左键点击球体: 展开交流界面
    echo   • 右键点击球体: 显示功能菜单
    echo   • 鼠标悬停: 增强发光效果
) else (
    echo.
    echo 启动失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo 按任意键退出...
pause >nul