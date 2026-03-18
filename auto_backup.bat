@echo off
echo OpenGodOS 自动备份系统
echo ========================================
echo 备份时间: %date% %time%
echo.

REM 设置Python路径
set PYTHON_PATH=python

REM 运行备份系统
echo 正在创建每日备份...
%PYTHON_PATH% backup_system.py --daily

if %errorlevel% equ 0 (
    echo 备份成功完成！
) else (
    echo 备份失败！
    pause
    exit /b 1
)

echo.
echo 备份完成，按任意键退出...
pause >nul