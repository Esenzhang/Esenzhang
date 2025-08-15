#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态IP轮换点击广告联盟网站链接脚本程序
支持指纹浏览器、动态IP轮换、多窗口管理
整合GUI示例图片的所有功能
"""

import sys
import os
import json
import threading
import time
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                             QTextEdit, QPushButton, QSpinBox, QComboBox, 
                             QProgressBar, QTabWidget, QGroupBox, QCheckBox,
                             QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
                             QRadioButton, QButtonGroup, QSplitter, QListWidget,
                             QListWidgetItem, QFrame, QScrollArea)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
import random
import psutil

class BrowserManager:
    """浏览器管理器"""
    
    def __init__(self):
        self.drivers = []
        self.proxy_list = []
        self.user_agents = []
        self.is_running = False
        
    def load_proxies(self, proxy_file):
        """加载代理列表"""
        try:
            with open(proxy_file, 'r', encoding='utf-8') as f:
                self.proxy_list = [line.strip() for line in f if line.strip()]
            return len(self.proxy_list)
        except Exception as e:
            print(f"加载代理文件失败: {e}")
            return 0
    
    def load_user_agents(self, ua_file):
        """加载用户代理列表"""
        try:
            with open(ua_file, 'r', encoding='utf-8') as f:
                self.user_agents = [line.strip() for line in f if line.strip()]
            return len(self.user_agents)
        except Exception as e:
            print(f"加载UA文件失败: {e}")
            return 0
    
    def create_driver(self, proxy=None, user_agent=None, headless=False):
        """创建浏览器驱动"""
        try:
            options = Options()
            
            # 设置用户代理
            if user_agent:
                options.add_argument(f'--user-agent={user_agent}')
            
            # 设置代理
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
            
            # 指纹浏览器设置
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 无头模式
            if headless:
                options.add_argument('--headless')
            
            # 创建驱动
            driver = uc.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
        except Exception as e:
            print(f"创建浏览器驱动失败: {e}")
            return None
    
    def close_all_drivers(self):
        """关闭所有浏览器驱动"""
        for driver in self.drivers:
            try:
                driver.quit()
            except:
                pass
        self.drivers.clear()

class ClickWorker(QThread):
    """点击工作线程"""
    
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    success_count_updated = pyqtSignal(int)
    failure_count_updated = pyqtSignal(int)
    stats_updated = pyqtSignal(dict)
    
    def __init__(self, target_url, proxy_list, user_agents, window_count, 
                 task_type, ad_platform, source_site, click_interval, 
                 is_real_person, undertake_platform):
        super().__init__()
        self.target_url = target_url
        self.proxy_list = proxy_list
        self.user_agents = user_agents
        self.window_count = window_count
        self.task_type = task_type
        self.ad_platform = ad_platform
        self.source_site = source_site
        self.click_interval = click_interval
        self.is_real_person = is_real_person
        self.undertake_platform = undertake_platform
        self.is_running = False
        self.success_count = 0
        self.failure_count = 0
        self.stats_data = []
        
    def run(self):
        """运行点击任务"""
        self.is_running = True
        drivers = []
        
        try:
            # 创建多个浏览器窗口
            for i in range(self.window_count):
                if not self.is_running:
                    break
                    
                # 选择代理和UA
                proxy = random.choice(self.proxy_list) if self.proxy_list else None
                user_agent = random.choice(self.user_agents) if self.user_agents else None
                
                # 创建驱动
                driver = self.create_driver(proxy, user_agent)
                if driver:
                    drivers.append(driver)
                    self.log_updated.emit(f"窗口 {i+1} 创建成功，代理: {proxy}")
                    
                    # 在新线程中执行点击
                    click_thread = threading.Thread(
                        target=self.perform_click,
                        args=(driver, i+1)
                    )
                    click_thread.daemon = True
                    click_thread.start()
                
                time.sleep(1)  # 避免同时启动过多窗口
            
            # 等待所有点击完成
            while self.is_running and any(driver.current_url != "data:," for driver in drivers):
                time.sleep(2)
                
        except Exception as e:
            self.log_updated.emit(f"执行过程中出错: {e}")
        finally:
            # 清理资源
            for driver in drivers:
                try:
                    driver.quit()
                except:
                    pass
            self.is_running = False
    
    def create_driver(self, proxy, user_agent):
        """创建浏览器驱动"""
        try:
            options = Options()
            
            if user_agent:
                options.add_argument(f'--user-agent={user_agent}')
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = uc.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
        except Exception as e:
            self.log_updated.emit(f"创建驱动失败: {e}")
            return None
    
    def perform_click(self, driver, window_id):
        """执行点击操作"""
        try:
            self.log_updated.emit(f"窗口 {window_id} 开始访问目标网站")
            
            # 访问目标网站
            driver.get(self.target_url)
            
            # 等待页面加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 随机等待时间（模拟真实用户行为）
            if self.is_real_person:
                wait_time = random.uniform(3, 8)
                time.sleep(wait_time)
            
            # 查找并点击广告链接
            ad_links = driver.find_elements(By.TAG_NAME, "a")
            clicked = False
            
            for link in ad_links:
                if not self.is_running:
                    break
                    
                try:
                    href = link.get_attribute("href")
                    if href and ("ad" in href.lower() or "click" in href.lower() or "banner" in href.lower()):
                        link.click()
                        self.log_updated.emit(f"窗口 {window_id} 成功点击广告链接: {href}")
                        clicked = True
                        self.success_count += 1
                        self.success_count_updated.emit(self.success_count)
                        
                        # 记录统计信息
                        stats = {
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'window_id': window_id,
                            'status': '成功',
                            'details': f'点击链接: {href}'
                        }
                        self.stats_data.append(stats)
                        self.stats_updated.emit(stats)
                        break
                except:
                    continue
            
            if not clicked:
                self.log_updated.emit(f"窗口 {window_id} 未找到可点击的广告链接")
                self.failure_count += 1
                self.failure_count_updated.emit(self.failure_count)
                
                # 记录失败统计
                stats = {
                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'window_id': window_id,
                    'status': '失败',
                    'details': '未找到可点击的广告链接'
                }
                self.stats_data.append(stats)
                self.stats_updated.emit(stats)
            
            # 保持窗口打开一段时间
            time.sleep(random.uniform(5, 15))
            
        except Exception as e:
            self.log_updated.emit(f"窗口 {window_id} 执行失败: {e}")
            self.failure_count += 1
            self.failure_count_updated.emit(self.failure_count)
            
            # 记录错误统计
            stats = {
                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'window_id': window_id,
                'status': '错误',
                'details': str(e)
            }
            self.stats_data.append(stats)
            self.stats_updated.emit(stats)
    
    def stop(self):
        """停止任务"""
        self.is_running = False

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.browser_manager = BrowserManager()
        self.click_worker = None
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("动态IP轮换点击广告联盟网站链接脚本程序")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout()
        
        # 创建左侧配置面板
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # 创建右侧文件管理面板
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        central_widget.setLayout(main_layout)
        
        # 状态栏
        self.statusBar().showMessage("程序就绪")
        
        # 定时器更新系统信息
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_info)
        self.timer.start(5000)  # 每5秒更新一次
        
    def create_left_panel(self):
        """创建左侧配置面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 任务类型选择
        task_group = QGroupBox("任务类型选择")
        task_layout = QVBoxLayout()
        
        self.task_type_group = QButtonGroup()
        task_types = ["Russia Trafbit", "Short Link", "Download", "Advertising Alliance"]
        for task_type in task_types:
            radio = QRadioButton(task_type)
            self.task_type_group.addButton(radio)
            task_layout.addWidget(radio)
            if task_type == "Advertising Alliance":
                radio.setChecked(True)
        
        task_group.setLayout(task_layout)
        layout.addWidget(task_group)
        
        # 广告平台选择
        platform_group = QGroupBox("广告平台选择")
        platform_layout = QVBoxLayout()
        
        self.platform_group = QButtonGroup()
        platforms = ["Google Adsense", "PopCash"]
        for platform in platforms:
            radio = QRadioButton(platform)
            self.platform_group.addButton(radio)
            platform_layout.addWidget(radio)
            if platform == "PopCash":
                radio.setChecked(True)
        
        platform_group.setLayout(platform_layout)
        layout.addWidget(platform_group)
        
        # 页面URL配置
        url_group = QGroupBox("页面URL配置")
        url_layout = QGridLayout()
        
        url_layout.addWidget(QLabel("Page Url:"), 0, 0)
        self.page_url_edit = QLineEdit()
        self.page_url_edit.setPlaceholderText("请输入目标网站URL")
        url_layout.addWidget(self.page_url_edit, 0, 1)
        
        self.page_url_browse_btn = QPushButton("编辑")
        self.page_url_browse_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView))
        self.page_url_browse_btn.clicked.connect(self.browse_page_url)
        url_layout.addWidget(self.page_url_browse_btn, 0, 2)
        
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # 流量来源配置
        source_group = QGroupBox("流量来源配置")
        source_layout = QGridLayout()
        
        source_layout.addWidget(QLabel("Traffic Source:"), 0, 0)
        self.traffic_source_edit = QLineEdit()
        self.traffic_source_edit.setPlaceholderText("请输入流量来源")
        source_layout.addWidget(self.traffic_source_edit, 0, 1)
        
        self.traffic_source_browse_btn = QPushButton("编辑")
        self.traffic_source_browse_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView))
        self.traffic_source_browse_btn.clicked.connect(self.browse_traffic_source)
        source_layout.addWidget(self.traffic_source_browse_btn, 0, 2)
        
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # 窗口数量配置
        window_group = QGroupBox("窗口数量配置")
        window_layout = QGridLayout()
        
        window_layout.addWidget(QLabel("Thread Number (窗口数量):"), 0, 0)
        self.window_count_spin = QSpinBox()
        self.window_count_spin.setRange(1, 50)
        self.window_count_spin.setValue(4)
        window_layout.addWidget(self.window_count_spin, 0, 1)
        
        window_group.setLayout(window_layout)
        layout.addWidget(window_group)
        
        # 承接平台配置
        undertake_group = QGroupBox("承接平台配置")
        undertake_layout = QGridLayout()
        
        undertake_layout.addWidget(QLabel("Undertake Platform:"), 0, 0)
        self.undertake_combo = QComboBox()
        self.undertake_combo.addItems(["direct", "proxy", "vpn"])
        undertake_layout.addWidget(self.undertake_combo, 0, 1)
        
        undertake_group.setLayout(undertake_layout)
        layout.addWidget(undertake_group)
        
        # 真实人模拟配置
        person_group = QGroupBox("真实人模拟配置")
        person_layout = QGridLayout()
        
        person_layout.addWidget(QLabel("Is Real Person Simulation:"), 0, 0)
        self.real_person_combo = QComboBox()
        self.real_person_combo.addItems(["Yes", "No"])
        person_layout.addWidget(self.real_person_combo, 0, 1)
        
        person_group.setLayout(person_layout)
        layout.addWidget(person_group)
        
        # 运行控制按钮
        control_group = QGroupBox("运行控制")
        control_layout = QVBoxLayout()
        
        self.run_btn = QPushButton("Run")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.run_btn.clicked.connect(self.start_clicking)
        control_layout.addWidget(self.run_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        """创建右侧文件管理面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 文件列表标题
        title_label = QLabel("文件管理")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setAlternatingRowColors(True)
        self.file_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:alternate {
                background-color: #f9f9f9;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        
        # 添加示例文件
        self.add_sample_files()
        
        layout.addWidget(self.file_list)
        
        # 文件操作按钮
        file_btn_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_file_list)
        file_btn_layout.addWidget(self.refresh_btn)
        
        self.add_file_btn = QPushButton("添加文件")
        self.add_file_btn.clicked.connect(self.add_file)
        file_btn_layout.addWidget(self.add_file_btn)
        
        layout.addLayout(file_btn_layout)
        
        panel.setLayout(layout)
        return panel
    
    def add_sample_files(self):
        """添加示例文件到列表"""
        sample_files = [
            "ip5.txt",
            "popUrl.txt", 
            "POP网站设置.docx",
            "ref.txt",
            "Windows 谷歌UA.txt",
            "安卓UA.txt"
        ]
        
        for file_name in sample_files:
            item = QListWidgetItem(file_name)
            if "UA" in file_name:
                item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView))
            elif "ip" in file_name.lower():
                item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
            else:
                item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogContentsView))
            self.file_list.addItem(item)
    
    def browse_page_url(self):
        """浏览页面URL文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择页面URL文件", "", "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            self.page_url_edit.setText(file_path)
            self.load_urls_from_file(file_path)
    
    def browse_traffic_source(self):
        """浏览流量来源文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择流量来源文件", "", "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            self.traffic_source_edit.setText(file_path)
            self.load_traffic_sources_from_file(file_path)
    
    def load_urls_from_file(self, file_path):
        """从文件加载URL列表"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            if urls:
                self.page_url_edit.setText(urls[0])  # 使用第一个URL
                self.log_message(f"已从文件加载 {len(urls)} 个URL")
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载URL文件失败: {e}")
    
    def load_traffic_sources_from_file(self, file_path):
        """从文件加载流量来源"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sources = [line.strip() for line in f if line.strip()]
            if sources:
                self.traffic_source_edit.setText(sources[0])  # 使用第一个来源
                self.log_message(f"已从文件加载 {len(sources)} 个流量来源")
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载流量来源文件失败: {e}")
    
    def refresh_file_list(self):
        """刷新文件列表"""
        self.file_list.clear()
        self.add_sample_files()
        self.log_message("文件列表已刷新")
    
    def add_file(self):
        """添加文件到列表"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "所有文件 (*)"
        )
        if file_path:
            file_name = os.path.basename(file_path)
            item = QListWidgetItem(file_name)
            item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogContentsView))
            self.file_list.addItem(item)
            self.log_message(f"已添加文件: {file_name}")
    
    def start_clicking(self):
        """开始点击任务"""
        if not self.page_url_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入目标网站URL")
            return
        
        # 获取任务类型
        task_type = "Advertising Alliance"
        for button in self.task_type_group.buttons():
            if button.isChecked():
                task_type = button.text()
                break
        
        # 获取广告平台
        ad_platform = "PopCash"
        for button in self.platform_group.buttons():
            if button.isChecked():
                ad_platform = button.text()
                break
        
        # 获取其他参数
        target_url = self.page_url_edit.text().strip()
        source_site = self.traffic_source_edit.text().strip()
        window_count = self.window_count_spin.value()
        undertake_platform = self.undertake_combo.currentText()
        is_real_person = self.real_person_combo.currentText() == "Yes"
        
        # 检查代理和UA文件
        if not self.browser_manager.proxy_list:
            QMessageBox.warning(self, "警告", "请先加载代理文件")
            return
        
        if not self.browser_manager.user_agents:
            QMessageBox.warning(self, "警告", "请先加载用户代理文件")
            return
        
        # 创建并启动工作线程
        self.click_worker = ClickWorker(
            target_url,
            self.browser_manager.proxy_list,
            self.browser_manager.user_agents,
            window_count,
            task_type,
            ad_platform,
            source_site,
            3,  # 默认点击间隔
            is_real_person,
            undertake_platform
        )
        
        # 连接信号
        self.click_worker.log_updated.connect(self.log_message)
        self.click_worker.success_count_updated.connect(self.update_success_count)
        self.click_worker.failure_count_updated.connect(self.update_failure_count)
        self.click_worker.stats_updated.connect(self.update_stats)
        
        # 启动线程
        self.click_worker.start()
        
        # 更新UI状态
        self.run_btn.setEnabled(False)
        self.run_btn.setText("运行中...")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
        """)
        
        self.log_message("开始执行点击任务")
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # 这里可以添加日志显示逻辑
        print(log_entry)
    
    def update_success_count(self, count):
        """更新成功次数"""
        self.log_message(f"成功点击次数: {count}")
    
    def update_failure_count(self, count):
        """更新失败次数"""
        self.log_message(f"失败点击次数: {count}")
    
    def update_stats(self, stats):
        """更新统计信息"""
        self.log_message(f"统计更新: {stats['window_id']} - {stats['status']}")
    
    def update_system_info(self):
        """更新系统信息"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 更新状态栏
            self.statusBar().showMessage(f"CPU: {cpu_percent:.1f}% | 内存: {memory_percent:.1f}% | 程序运行中")
            
        except Exception as e:
            pass

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("动态IP轮换点击脚本")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("ClickScript")
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main()