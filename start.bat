@echo off
chcp 65001 >nul
title 动态IP轮换点击广告联盟网站链接脚本程序

echo ========================================
echo 动态IP轮换点击广告联盟网站链接脚本程序
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python环境检查通过
echo.

echo 正在检查依赖包...
echo 正在安装/更新依赖包...
pip install -r requirements.txt

if errorlevel 1 (
    echo 警告: 部分依赖包安装失败，程序可能无法正常运行
    echo 请检查网络连接或手动安装依赖包
    pause
)

echo.
echo 正在启动程序...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
)

echo.
echo 程序已退出
pause