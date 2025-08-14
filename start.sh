#!/bin/bash

echo "========================================"
echo "动态IP轮换点击广告联盟网站链接脚本程序"
echo "========================================"
echo

echo "正在检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3环境，请先安装Python 3.8+"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

echo "Python环境检查通过"
echo

echo "正在检查依赖包..."
echo "正在安装/更新依赖包..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "警告: 部分依赖包安装失败，程序可能无法正常运行"
    echo "请检查网络连接或手动安装依赖包"
    read -p "按回车键继续..."
fi

echo
echo "正在启动程序..."
echo

python3 main.py

if [ $? -ne 0 ]; then
    echo
    echo "程序运行出错，请检查错误信息"
    read -p "按回车键继续..."
fi

echo
echo "程序已退出"
read -p "按回车键继续..."