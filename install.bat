@echo off
chcp 65001 >nul
title 动态IP轮换点击脚本 - 安装程序

echo ========================================
echo 动态IP轮换点击广告联盟网站链接脚本程序
echo 安装程序
echo ========================================
echo.

echo 正在检查系统环境...
echo.

REM 检查Python版本
echo [1/5] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python环境
    echo.
    echo 请先安装Python 3.8或更高版本：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载最新版本的Python
    echo 3. 运行安装程序时务必勾选"Add Python to PATH"
    echo 4. 安装完成后重新运行此安装程序
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Python环境检查通过
    python --version
)

echo.
echo [2/5] 检查pip包管理器...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip包管理器不可用
    echo 正在尝试修复...
    python -m ensurepip --upgrade
) else (
    echo ✅ pip包管理器可用
    python -m pip --version
)

echo.
echo [3/5] 升级pip到最新版本...
python -m pip install --upgrade pip

echo.
echo [4/5] 安装项目依赖包...
echo 正在安装依赖包，这可能需要几分钟时间...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ⚠️  部分依赖包安装失败
    echo 请检查网络连接或手动安装：
    echo.
    echo 手动安装命令：
    echo pip install selenium undetected-chromedriver PyQt6 requests beautifulsoup4 fake-useragent psutil
    echo.
    echo 如果继续遇到问题，请：
    echo 1. 检查网络连接
    echo 2. 尝试使用国内镜像源：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
    echo 3. 检查防火墙设置
    echo.
    pause
) else (
    echo ✅ 依赖包安装完成
)

echo.
echo [5/5] 检查Chrome浏览器...
reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未检测到Chrome浏览器
    echo 请安装Chrome浏览器以确保程序正常运行
    echo 下载地址: https://www.google.com/chrome/
) else (
    echo ✅ Chrome浏览器已安装
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 现在您可以：
echo 1. 双击 start.bat 启动程序
echo 2. 或在命令行中运行 python main.py
echo.
echo 使用前请确保：
echo - 已配置代理文件 (sample_proxies.txt)
echo - 已配置用户代理文件 (sample_user_agents.txt)
echo - 已设置目标网站URL
echo.
echo 祝您使用愉快！
echo.
pause