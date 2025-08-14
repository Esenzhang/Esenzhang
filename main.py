#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态IP轮换点击广告联盟网站链接脚本程序
支持指纹浏览器、动态IP轮换、多窗口管理
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
                             QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap
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
    
    def create_driver(self, proxy=None, user_agent=None):
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
    
    def __init__(self, target_url, proxy_list, user_agents, window_count):
        super().__init__()
        self.target_url = target_url
        self.proxy_list = proxy_list
        self.user_agents = user_agents
        self.window_count = window_count
        self.is_running = False
        self.success_count = 0
        self.failure_count = 0
        
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
            
            # 随机等待时间
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
                        break
                except:
                    continue
            
            if not clicked:
                self.log_updated.emit(f"窗口 {window_id} 未找到可点击的广告链接")
                self.failure_count += 1
                self.failure_count_updated.emit(self.failure_count)
            
            # 保持窗口打开一段时间
            time.sleep(random.uniform(5, 15))
            
        except Exception as e:
            self.log_updated.emit(f"窗口 {window_id} 执行失败: {e}")
            self.failure_count += 1
            self.failure_count_updated.emit(self.failure_count)
    
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
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 主控制标签页
        main_tab = self.create_main_tab()
        tab_widget.addTab(main_tab, "主控制")
        
        # 配置标签页
        config_tab = self.create_config_tab()
        tab_widget.addTab(config_tab, "配置管理")
        
        # 日志标签页
        log_tab = self.create_log_tab()
        tab_widget.addTab(log_tab, "运行日志")
        
        # 统计标签页
        stats_tab = self.create_stats_tab()
        tab_widget.addTab(stats_tab, "成功率统计")
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)
        central_widget.setLayout(main_layout)
        
        # 状态栏
        self.statusBar().showMessage("程序就绪")
        
        # 定时器更新系统信息
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_info)
        self.timer.start(5000)  # 每5秒更新一次
        
    def create_main_tab(self):
        """创建主控制标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 目标网站配置
        target_group = QGroupBox("目标网站配置")
        target_layout = QGridLayout()
        
        target_layout.addWidget(QLabel("目标网站URL:"), 0, 0)
        self.target_url_edit = QLineEdit()
        self.target_url_edit.setPlaceholderText("请输入目标网站URL")
        target_layout.addWidget(self.target_url_edit, 0, 1)
        
        target_layout.addWidget(QLabel("来源网站:"), 1, 0)
        self.source_site_edit = QLineEdit()
        self.source_site_edit.setPlaceholderText("请输入来源网站")
        target_layout.addWidget(self.source_site_edit, 1, 1)
        
        target_group.setLayout(target_layout)
        layout.addWidget(target_group)
        
        # 运行参数配置
        run_group = QGroupBox("运行参数配置")
        run_layout = QGridLayout()
        
        run_layout.addWidget(QLabel("窗口数量:"), 0, 0)
        self.window_count_spin = QSpinBox()
        self.window_count_spin.setRange(1, 50)
        self.window_count_spin.setValue(5)
        run_layout.addWidget(self.window_count_spin, 0, 1)
        
        run_layout.addWidget(QLabel("点击间隔(秒):"), 0, 2)
        self.click_interval_spin = QSpinBox()
        self.click_interval_spin.setRange(1, 60)
        self.click_interval_spin.setValue(3)
        run_layout.addWidget(self.click_interval_spin, 0, 3)
        
        run_group.setLayout(run_layout)
        layout.addWidget(run_group)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("开始运行")
        self.start_btn.clicked.connect(self.start_clicking)
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-size: 14px; padding: 10px; }")
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止运行")
        self.stop_btn.clicked.connect(self.stop_clicking)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-size: 14px; padding: 10px; }")
        control_layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton("清空日志")
        self.clear_btn.clicked.connect(self.clear_logs)
        self.clear_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-size: 14px; padding: 10px; }")
        control_layout.addWidget(self.clear_btn)
        
        layout.addLayout(control_layout)
        
        # 实时状态显示
        status_group = QGroupBox("实时状态")
        status_layout = QGridLayout()
        
        status_layout.addWidget(QLabel("运行状态:"), 0, 0)
        self.status_label = QLabel("未运行")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.status_label, 0, 1)
        
        status_layout.addWidget(QLabel("CPU使用率:"), 0, 2)
        self.cpu_label = QLabel("0%")
        status_layout.addWidget(self.cpu_label, 0, 3)
        
        status_layout.addWidget(QLabel("内存使用率:"), 1, 0)
        self.memory_label = QLabel("0%")
        status_layout.addWidget(self.memory_label, 1, 1)
        
        status_layout.addWidget(QLabel("网络连接数:"), 1, 2)
        self.network_label = QLabel("0")
        status_layout.addWidget(self.network_label, 1, 3)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_config_tab(self):
        """创建配置管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 代理配置
        proxy_group = QGroupBox("代理配置")
        proxy_layout = QGridLayout()
        
        proxy_layout.addWidget(QLabel("代理文件路径:"), 0, 0)
        self.proxy_path_edit = QLineEdit()
        self.proxy_path_edit.setPlaceholderText("请选择代理文件")
        proxy_layout.addWidget(self.proxy_path_edit, 0, 1)
        
        self.proxy_browse_btn = QPushButton("浏览")
        self.proxy_browse_btn.clicked.connect(self.browse_proxy_file)
        proxy_layout.addWidget(self.proxy_browse_btn, 0, 2)
        
        proxy_layout.addWidget(QLabel("代理数量:"), 1, 0)
        self.proxy_count_label = QLabel("0")
        proxy_layout.addWidget(self.proxy_count_label, 1, 1)
        
        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)
        
        # UA配置
        ua_group = QGroupBox("用户代理配置")
        ua_layout = QGridLayout()
        
        ua_layout.addWidget(QLabel("UA文件路径:"), 0, 0)
        self.ua_path_edit = QLineEdit()
        self.ua_path_edit.setPlaceholderText("请选择UA文件")
        ua_layout.addWidget(self.ua_path_edit, 0, 1)
        
        self.ua_browse_btn = QPushButton("浏览")
        self.ua_browse_btn.clicked.connect(self.browse_ua_file)
        ua_layout.addWidget(self.ua_browse_btn, 0, 2)
        
        ua_layout.addWidget(QLabel("UA数量:"), 1, 0)
        self.ua_count_label = QLabel("0")
        ua_layout.addWidget(self.ua_count_label, 1, 1)
        
        ua_group.setLayout(ua_layout)
        layout.addWidget(ua_group)
        
        # 高级配置
        advanced_group = QGroupBox("高级配置")
        advanced_layout = QGridLayout()
        
        self.headless_checkbox = QCheckBox("无头模式")
        advanced_layout.addWidget(self.headless_checkbox, 0, 0)
        
        self.auto_rotate_checkbox = QCheckBox("自动轮换IP")
        self.auto_rotate_checkbox.setChecked(True)
        advanced_layout.addWidget(self.auto_rotate_checkbox, 0, 1)
        
        self.random_delay_checkbox = QCheckBox("随机延迟")
        self.random_delay_checkbox.setChecked(True)
        advanced_layout.addWidget(self.random_delay_checkbox, 0, 2)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # 配置操作按钮
        config_btn_layout = QHBoxLayout()
        
        self.load_config_btn = QPushButton("加载配置")
        self.load_config_btn.clicked.connect(self.load_config)
        config_btn_layout.addWidget(self.load_config_btn)
        
        self.save_config_btn = QPushButton("保存配置")
        self.save_config_btn.clicked.connect(self.save_config)
        config_btn_layout.addWidget(self.save_config_btn)
        
        self.reset_config_btn = QPushButton("重置配置")
        self.reset_config_btn.clicked.connect(self.reset_config)
        config_btn_layout.addWidget(self.reset_config_btn)
        
        layout.addLayout(config_btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_log_tab(self):
        """创建运行日志标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.log_text)
        
        # 日志控制按钮
        log_btn_layout = QHBoxLayout()
        
        self.export_log_btn = QPushButton("导出日志")
        self.export_log_btn.clicked.connect(self.export_log)
        log_btn_layout.addWidget(self.export_log_btn)
        
        self.clear_log_btn = QPushButton("清空日志")
        self.clear_log_btn.clicked.connect(self.clear_logs)
        log_btn_layout.addWidget(self.clear_log_btn)
        
        layout.addLayout(log_btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_stats_tab(self):
        """创建成功率统计标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 统计信息显示
        stats_group = QGroupBox("点击统计")
        stats_layout = QGridLayout()
        
        stats_layout.addWidget(QLabel("总点击次数:"), 0, 0)
        self.total_clicks_label = QLabel("0")
        stats_layout.addWidget(self.total_clicks_label, 0, 1)
        
        stats_layout.addWidget(QLabel("成功次数:"), 0, 2)
        self.success_clicks_label = QLabel("0")
        self.success_clicks_label.setStyleSheet("color: green; font-weight: bold;")
        stats_layout.addWidget(self.success_clicks_label, 0, 3)
        
        stats_layout.addWidget(QLabel("失败次数:"), 1, 0)
        self.failure_clicks_label = QLabel("0")
        self.failure_clicks_label.setStyleSheet("color: red; font-weight: bold;")
        stats_layout.addWidget(self.failure_clicks_label, 1, 1)
        
        stats_layout.addWidget(QLabel("成功率:"), 1, 2)
        self.success_rate_label = QLabel("0%")
        self.success_rate_label.setStyleSheet("color: blue; font-weight: bold; font-size: 16px;")
        stats_layout.addWidget(self.success_rate_label, 1, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # 成功率进度条
        progress_group = QGroupBox("成功率可视化")
        progress_layout = QVBoxLayout()
        
        self.success_progress = QProgressBar()
        self.success_progress.setRange(0, 100)
        self.success_progress.setValue(0)
        self.success_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.success_progress)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 详细统计表格
        table_group = QGroupBox("详细统计")
        table_layout = QVBoxLayout()
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(["时间", "窗口ID", "状态", "详情"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.stats_table)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        widget.setLayout(layout)
        return widget
    
    def browse_proxy_file(self):
        """浏览代理文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择代理文件", "", "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            self.proxy_path_edit.setText(file_path)
            count = self.browser_manager.load_proxies(file_path)
            self.proxy_count_label.setText(str(count))
            self.log_message(f"已加载 {count} 个代理")
    
    def browse_ua_file(self):
        """浏览UA文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择UA文件", "", "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            self.ua_path_edit.setText(file_path)
            count = self.browser_manager.load_user_agents(file_path)
            self.ua_count_label.setText(str(count))
            self.log_message(f"已加载 {count} 个用户代理")
    
    def start_clicking(self):
        """开始点击任务"""
        if not self.target_url_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入目标网站URL")
            return
        
        if not self.browser_manager.proxy_list:
            QMessageBox.warning(self, "警告", "请先加载代理文件")
            return
        
        if not self.browser_manager.user_agents:
            QMessageBox.warning(self, "警告", "请先加载用户代理文件")
            return
        
        # 创建并启动工作线程
        self.click_worker = ClickWorker(
            self.target_url_edit.text().strip(),
            self.browser_manager.proxy_list,
            self.browser_manager.user_agents,
            self.window_count_spin.value()
        )
        
        # 连接信号
        self.click_worker.progress_updated.connect(self.update_progress)
        self.click_worker.log_updated.connect(self.log_message)
        self.click_worker.success_count_updated.connect(self.update_success_count)
        self.click_worker.failure_count_updated.connect(self.update_failure_count)
        
        # 启动线程
        self.click_worker.start()
        
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("运行中")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        
        self.log_message("开始执行点击任务")
    
    def stop_clicking(self):
        """停止点击任务"""
        if self.click_worker:
            self.click_worker.stop()
            self.click_worker.wait()
            self.click_worker = None
        
        # 更新UI状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("已停止")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        self.log_message("点击任务已停止")
    
    def update_progress(self, value):
        """更新进度"""
        pass  # 可以在这里添加进度条更新逻辑
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        
        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def update_success_count(self, count):
        """更新成功次数"""
        self.success_clicks_label.setText(str(count))
        self.update_success_rate()
    
    def update_failure_count(self, count):
        """更新失败次数"""
        self.failure_clicks_label.setText(str(count))
        self.update_success_rate()
    
    def update_success_rate(self):
        """更新成功率"""
        success = int(self.success_clicks_label.text())
        failure = int(self.failure_clicks_label.text())
        total = success + failure
        
        if total > 0:
            rate = (success / total) * 100
            self.success_rate_label.setText(f"{rate:.1f}%")
            self.success_progress.setValue(int(rate))
        else:
            self.success_rate_label.setText("0%")
            self.success_progress.setValue(0)
        
        self.total_clicks_label.setText(str(total))
    
    def clear_logs(self):
        """清空日志"""
        self.log_text.clear()
        self.log_message("日志已清空")
    
    def export_log(self):
        """导出日志"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出日志", f"click_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 
            "文本文件 (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(self, "成功", f"日志已导出到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")
    
    def load_config(self):
        """加载配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载配置", "", "JSON文件 (*.json);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 应用配置
                self.target_url_edit.setText(config.get('target_url', ''))
                self.source_site_edit.setText(config.get('source_site', ''))
                self.window_count_spin.setValue(config.get('window_count', 5))
                self.click_interval_spin.setValue(config.get('click_interval', 3))
                self.proxy_path_edit.setText(config.get('proxy_path', ''))
                self.ua_path_edit.setText(config.get('ua_path', ''))
                
                QMessageBox.information(self, "成功", "配置加载成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置", f"click_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 
            "JSON文件 (*.json)"
        )
        if file_path:
            try:
                config = {
                    'target_url': self.target_url_edit.text(),
                    'source_site': self.source_site_edit.text(),
                    'window_count': self.window_count_spin.value(),
                    'click_interval': self.click_interval_spin.value(),
                    'proxy_path': self.proxy_path_edit.text(),
                    'ua_path': self.ua_path_edit.text(),
                    'headless': self.headless_checkbox.isChecked(),
                    'auto_rotate': self.auto_rotate_checkbox.isChecked(),
                    'random_delay': self.random_delay_checkbox.isChecked()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "成功", f"配置已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存配置失败: {e}")
    
    def reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(
            self, "确认", "确定要重置所有配置吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.target_url_edit.clear()
            self.source_site_edit.clear()
            self.window_count_spin.setValue(5)
            self.click_interval_spin.setValue(3)
            self.proxy_path_edit.clear()
            self.ua_path_edit.clear()
            self.headless_checkbox.setChecked(False)
            self.auto_rotate_checkbox.setChecked(True)
            self.random_delay_checkbox.setChecked(True)
            
            self.proxy_count_label.setText("0")
            self.ua_count_label.setText("0")
            
            QMessageBox.information(self, "成功", "配置已重置")
    
    def update_system_info(self):
        """更新系统信息"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_label.setText(f"{cpu_percent:.1f}%")
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_label.setText(f"{memory_percent:.1f}%")
            
            # 网络连接数
            connections = len(psutil.net_connections())
            self.network_label.setText(str(connections))
            
        except Exception as e:
            pass
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.click_worker and self.click_worker.is_running:
            reply = QMessageBox.question(
                self, "确认", "任务正在运行中，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_clicking()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("动态IP轮换点击脚本")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ClickScript")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main()