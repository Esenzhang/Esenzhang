# PyCharm 项目配置指南

本文档详细说明如何在最新版本的PyCharm中配置和运行动态IP轮换点击脚本项目。

## 🚀 环境要求

- **PyCharm版本**: PyCharm Professional 2023.3+ 或 PyCharm Community 2023.3+
- **Python版本**: Python 3.8+
- **操作系统**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

## 📋 安装步骤

### 1. 下载并安装PyCharm

1. 访问 [JetBrains官网](https://www.jetbrains.com/pycharm/) 下载最新版本
2. 选择Professional或Community版本（推荐Professional，功能更完整）
3. 运行安装程序，按照向导完成安装

### 2. 安装Python环境

#### Windows
1. 访问 [Python官网](https://www.python.org/downloads/) 下载最新版本
2. 运行安装程序，**务必勾选"Add Python to PATH"**
3. 验证安装: 打开命令提示符，输入 `python --version`

#### macOS
```bash
# 使用Homebrew安装
brew install python3

# 或从官网下载安装包
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## 🔧 PyCharm项目配置

### 1. 打开项目

1. 启动PyCharm
2. 选择 "Open" 或 "Open an existing project"
3. 导航到项目文件夹，选择包含 `main.py` 的目录
4. 点击 "OK" 打开项目

### 2. 配置Python解释器

1. 打开 `File` → `Settings` (Windows/Linux) 或 `PyCharm` → `Preferences` (macOS)
2. 在左侧导航栏选择 `Project: [项目名]` → `Python Interpreter`
3. 点击齿轮图标，选择 "Add"
4. 选择 "System Interpreter"
5. 浏览到Python安装路径（通常在 `/usr/bin/python3` 或 `C:\Python3x\python.exe`）
6. 点击 "OK" 确认

### 3. 安装项目依赖

#### 方法1: 使用PyCharm终端
1. 在PyCharm底部打开 "Terminal" 标签页
2. 运行以下命令：
```bash
pip install -r requirements.txt
```

#### 方法2: 使用PyCharm包管理器
1. 打开 `File` → `Settings` → `Project: [项目名]` → `Python Interpreter`
2. 点击 "+" 按钮
3. 搜索并安装以下包：
   - selenium
   - undetected-chromedriver
   - PyQt6
   - requests
   - beautifulsoup4
   - fake-useragent
   - psutil

### 4. 配置运行配置

1. 点击顶部工具栏的 "Add Configuration" 或 "Edit Configurations"
2. 点击 "+" 按钮，选择 "Python"
3. 配置以下参数：
   - **Name**: `main`
   - **Script path**: 选择项目中的 `main.py` 文件
   - **Working directory**: 设置为项目根目录
   - **Python interpreter**: 选择之前配置的Python解释器
4. 点击 "OK" 保存配置

## 🎯 推荐PyCharm插件

### 必需插件
- **Python**: 内置，提供Python语言支持
- **PyQt6**: 提供PyQt6框架支持

### 推荐插件
- **Rainbow Brackets**: 彩色括号匹配
- **Material Theme UI**: 现代化界面主题
- **Key Promoter X**: 快捷键提示
- **String Manipulation**: 字符串处理工具
- **Git Integration**: Git版本控制集成

### 安装插件步骤
1. 打开 `File` → `Settings` → `Plugins`
2. 在 "Marketplace" 标签页搜索插件名称
3. 点击 "Install" 安装
4. 重启PyCharm

## ⚙️ 项目特定配置

### 1. 代码风格设置
1. 打开 `File` → `Settings` → `Editor` → `Code Style` → `Python`
2. 设置缩进为4个空格
3. 设置行长度为120字符

### 2. 导入优化
1. 打开 `File` → `Settings` → `Editor` → `Code Style` → `Python`
2. 在 "Imports" 标签页配置导入顺序

### 3. 代码检查
1. 打开 `File` → `Settings` → `Editor` → `Inspections`
2. 启用Python相关的代码检查规则

## 🚀 运行和调试

### 1. 运行程序
- 点击顶部工具栏的绿色运行按钮 ▶️
- 或使用快捷键 `Shift + F10`

### 2. 调试程序
- 点击顶部工具栏的绿色调试按钮 🐛
- 或使用快捷键 `Shift + F9`

### 3. 设置断点
- 在代码行号左侧点击设置断点
- 使用调试模式运行程序

## 🔍 常见问题解决

### 1. 模块导入错误
**问题**: `ModuleNotFoundError: No module named 'xxx'`
**解决**: 
1. 检查Python解释器配置
2. 在PyCharm终端中运行 `pip install xxx`
3. 重启PyCharm

### 2. PyQt6相关错误
**问题**: `ImportError: DLL load failed` (Windows)
**解决**:
1. 确保安装了Microsoft Visual C++ Redistributable
2. 重新安装PyQt6: `pip uninstall PyQt6 && pip install PyQt6`

### 3. Chrome驱动错误
**问题**: `WebDriverException: Message: unknown error: cannot find Chrome binary`
**解决**:
1. 确保系统已安装Chrome浏览器
2. 检查Chrome安装路径是否正确
3. 更新Chrome到最新版本

### 4. 权限错误
**问题**: `PermissionError: [Errno 13] Permission denied`
**解决**:
1. 以管理员身份运行PyCharm
2. 检查文件和目录权限
3. 使用虚拟环境

## 📚 调试技巧

### 1. 使用PyCharm调试器
- 设置断点观察变量值
- 使用 "Variables" 窗口查看局部变量
- 使用 "Watches" 窗口监控特定表达式

### 2. 日志输出
- 在代码中添加 `print()` 语句
- 使用Python的 `logging` 模块
- 查看PyCharm的 "Run" 窗口输出

### 3. 性能分析
- 使用PyCharm的 "Profiler" 工具
- 分析代码执行时间和内存使用

## 🎨 界面优化建议

### 1. 主题设置
1. 打开 `File` → `Settings` → `Appearance & Behavior` → `Appearance`
2. 选择喜欢的主题（推荐 "Darcula" 或 "Light"）

### 2. 字体设置
1. 打开 `File` → `Settings` → `Editor` → `Font`
2. 选择等宽字体（推荐 "Consolas" 或 "JetBrains Mono"）
3. 设置合适的字体大小

### 3. 快捷键自定义
1. 打开 `File` → `Settings` → `Keymap`
2. 根据个人习惯自定义快捷键

## 📖 学习资源

- [PyCharm官方文档](https://www.jetbrains.com/help/pycharm/)
- [Python官方教程](https://docs.python.org/3/tutorial/)
- [PyQt6官方文档](https://doc.qt.io/qtforpython/)
- [Selenium官方文档](https://selenium-python.readthedocs.io/)

## 🆘 获取帮助

如果遇到问题：
1. 查看PyCharm的错误日志
2. 搜索Stack Overflow相关问题
3. 查看项目README文档
4. 提交GitHub Issue

---

**注意**: 本指南基于PyCharm 2023.3版本编写，其他版本可能略有差异。