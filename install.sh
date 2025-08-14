#!/bin/bash

echo "========================================"
echo "动态IP轮换点击广告联盟网站链接脚本程序"
echo "安装程序"
echo "========================================"
echo

echo "正在检查系统环境..."
echo

# 检查Python版本
echo "[1/5] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3环境"
    echo
    echo "请先安装Python 3.8或更高版本："
    echo
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Ubuntu/Debian:"
        echo "  sudo apt update"
        echo "  sudo apt install python3 python3-pip python3-venv"
        echo
        echo "CentOS/RHEL:"
        echo "  sudo yum install python3 python3-pip"
        echo
        echo "Arch Linux:"
        echo "  sudo pacman -S python python-pip"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOS:"
        echo "  brew install python3"
        echo "  或从 https://www.python.org/downloads/ 下载安装包"
    fi
    echo
    echo "安装完成后重新运行此安装程序"
    exit 1
else
    echo "✅ Python环境检查通过"
    python3 --version
fi

echo
echo "[2/5] 检查pip包管理器..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip包管理器不可用"
    echo "正在尝试修复..."
    python3 -m ensurepip --upgrade
else
    echo "✅ pip包管理器可用"
    pip3 --version
fi

echo
echo "[3/5] 升级pip到最新版本..."
python3 -m pip install --upgrade pip

echo
echo "[4/5] 安装项目依赖包..."
echo "正在安装依赖包，这可能需要几分钟时间..."

# 尝试使用国内镜像源
echo "尝试使用国内镜像源安装..."
if pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt; then
    echo "✅ 依赖包安装完成"
else
    echo "尝试使用官方源安装..."
    if pip3 install -r requirements.txt; then
        echo "✅ 依赖包安装完成"
    else
        echo
        echo "⚠️  部分依赖包安装失败"
        echo "请检查网络连接或手动安装："
        echo
        echo "手动安装命令："
        echo "pip3 install selenium undetected-chromedriver PyQt6 requests beautifulsoup4 fake-useragent psutil"
        echo
        echo "如果继续遇到问题，请："
        echo "1. 检查网络连接"
        echo "2. 尝试使用其他镜像源："
        echo "   pip3 install -i https://pypi.douban.com/simple/ -r requirements.txt"
        echo "   pip3 install -i https://pypi.mirrors.ustc.edu.cn/simple/ -r requirements.txt"
        echo "3. 检查防火墙设置"
        echo "4. 尝试使用sudo权限安装"
        echo
        read -p "按回车键继续..."
    fi
fi

echo
echo "[5/5] 检查Chrome浏览器..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null; then
        echo "✅ Chrome/Chromium浏览器已安装"
    else
        echo "⚠️  未检测到Chrome浏览器"
        echo "请安装Chrome浏览器以确保程序正常运行："
        echo "Ubuntu/Debian: sudo apt install google-chrome-stable"
        echo "CentOS/RHEL: sudo yum install google-chrome-stable"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -d "/Applications/Google Chrome.app" ]; then
        echo "✅ Chrome浏览器已安装"
    else
        echo "⚠️  未检测到Chrome浏览器"
        echo "请从 https://www.google.com/chrome/ 下载安装"
    fi
fi

echo
echo "========================================"
echo "安装完成！"
echo "========================================"
echo
echo "现在您可以："
echo "1. 运行 ./start.sh 启动程序"
echo "2. 或在命令行中运行 python3 main.py"
echo
echo "使用前请确保："
echo "- 已配置代理文件 (sample_proxies.txt)"
echo "- 已配置用户代理文件 (sample_user_agents.txt)"
echo "- 已设置目标网站URL"
echo
echo "祝您使用愉快！"
echo
read -p "按回车键继续..."