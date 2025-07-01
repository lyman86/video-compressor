#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口类 - 应用程序的核心界面
"""

import json
import sys
import time
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QSplitter, QStatusBar, QMenuBar,
    QMenu, QMessageBox, QApplication, QProgressBar, QAction, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon, QPixmap


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化变量
        self.config = self.load_config()
        self.current_video_file = None
        self.compression_thread = None
        
        # 设置窗口基础属性
        self.setup_window()
        
        # 创建用户界面
        self.setup_ui()
        
        # 加载样式
        self.load_styles()
        
        # 连接信号和槽
        self.connect_signals()
        
        # 初始化FFmpeg状态
        self.check_ffmpeg_status()
    
    def setup_window(self):
        """设置窗口基础属性"""
        # 窗口标题和图标
        self.setWindowTitle(f"{self.config['app']['name']} v{self.config['app']['version']}")
        
        # 窗口大小和位置
        window_config = self.config['app']['window']
        self.resize(window_config['width'], window_config['height'])
        self.setMinimumSize(window_config['min_width'], window_config['min_height'])
        
        # 居中显示
        self.center_on_screen()
        
        # 设置窗口图标（如果存在）
        icon_path = Path("resources/icons/app_icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
    
    def center_on_screen(self):
        """将窗口居中显示"""
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        center_point = screen.center()
        window.moveCenter(center_point)
        self.move(window.topLeft())
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 创建顶部标题区域
        self.create_header_section(main_layout)
        
        # 创建主要内容区域
        self.create_main_content_area(main_layout)
        
        # 创建底部状态区域
        self.create_footer_section(main_layout)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_header_section(self, parent_layout):
        """创建顶部标题区域"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFrameStyle(QFrame.StyledPanel)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        # 应用标题和版本
        title_layout = QVBoxLayout()
        
        self.title_label = QLabel(self.config['app']['name'])
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignLeft)
        
        self.subtitle_label = QLabel("简单易用的视频压缩工具")
        self.subtitle_label.setObjectName("subtitleLabel")
        self.subtitle_label.setAlignment(Qt.AlignLeft)
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # FFmpeg状态指示器（可点击安装）
        self.ffmpeg_status_label = QPushButton("FFmpeg: 检查中...")
        self.ffmpeg_status_label.setObjectName("ffmpegStatus")
        self.ffmpeg_status_label.setToolTip("点击管理FFmpeg安装")
        self.ffmpeg_status_label.setStyleSheet("""
            QPushButton#ffmpegStatus {
                background-color: #f39c12; 
                color: white; 
                padding: 6px 12px; 
                border-radius: 4px;
                border: none;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton#ffmpegStatus:hover {
                background-color: #e67e22;
            }
        """)
        self.ffmpeg_status_label.clicked.connect(self.show_ffmpeg_info)
        header_layout.addWidget(self.ffmpeg_status_label)
        
        parent_layout.addWidget(header_frame)
    
    def create_main_content_area(self, parent_layout):
        """创建主要内容区域"""
        # 创建水平分割器
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setObjectName("mainSplitter")
        
        # 左侧：文件选择和预览区域
        left_widget = self.create_left_panel()
        main_splitter.addWidget(left_widget)
        
        # 右侧：压缩设置和控制区域
        right_widget = self.create_right_panel()
        main_splitter.addWidget(right_widget)
        
        # 设置分割器比例 (60% : 40%)
        main_splitter.setSizes([360, 240])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        
        parent_layout.addWidget(main_splitter, 1)
    
    def create_left_panel(self):
        """创建左侧面板 - 文件选择和预览"""
        left_frame = QFrame()
        left_frame.setObjectName("leftPanel")
        left_frame.setFrameStyle(QFrame.StyledPanel)
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(18, 18, 18, 18)  # 适中的边距
        left_layout.setSpacing(10)  # 适中的间距，避免组件过于紧密
        
        # 文件选择区域标题
        file_section_label = QLabel("📁 选择视频文件")
        file_section_label.setObjectName("sectionLabel")
        left_layout.addWidget(file_section_label)
        
        # 文件拖拽区域 - 使用自定义组件，设置弹性布局
        from app.widgets.file_drop_widget import FileDropWidget
        self.file_drop_area = FileDropWidget()
        self.file_drop_area.file_selected.connect(self.on_file_selected)
        # 设置弹性大小策略，最小高度降低以适配小窗口
        self.file_drop_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        left_layout.addWidget(self.file_drop_area, 3)  # 给予权重3，实现3:2比例
        
        # 文件信息显示区域
        info_section_label = QLabel("📊 文件信息")
        info_section_label.setObjectName("sectionLabel")
        left_layout.addWidget(info_section_label)
        
        self.video_info_frame = QFrame()
        self.video_info_frame.setObjectName("videoInfoFrame")
        self.video_info_frame.setFrameStyle(QFrame.StyledPanel)
        # 使用更灵活的高度设置，按3:2比例调整
        self.video_info_frame.setMinimumHeight(120)  # 按比例调整最小高度
        self.video_info_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        info_layout = QVBoxLayout(self.video_info_frame)
        info_layout.setContentsMargins(8, 8, 8, 8)  # 调整边距
        
        self.video_info_label = QLabel("请选择视频文件")
        self.video_info_label.setObjectName("videoInfoLabel")
        self.video_info_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # 顶部居中对齐
        self.video_info_label.setWordWrap(True)
        self.video_info_label.setTextFormat(Qt.RichText)  # 支持HTML格式
        self.video_info_label.setMinimumHeight(100)  # 减少最小高度
        self.video_info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        info_layout.addWidget(self.video_info_label)
        
        left_layout.addWidget(self.video_info_frame, 2)  # 给予权重2，更多空间
        
        return left_frame
    
    def create_right_panel(self):
        """创建右侧面板 - 压缩设置和控制"""
        right_frame = QFrame()
        right_frame.setObjectName("rightPanel")
        right_frame.setFrameStyle(QFrame.StyledPanel)
        
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)
        
        # 压缩设置区域标题
        settings_section_label = QLabel("⚙️ 压缩设置")
        settings_section_label.setObjectName("sectionLabel")
        right_layout.addWidget(settings_section_label)
        
        # 压缩设置组件
        from app.widgets.compression_settings_widget import CompressionSettingsWidget
        self.compression_settings = CompressionSettingsWidget()
        self.compression_settings.setObjectName("compressionSettings")
        self.compression_settings.settings_changed.connect(self.on_compression_settings_changed)
        
        right_layout.addWidget(self.compression_settings)
        
        # 控制按钮区域
        control_section_label = QLabel("🎬 操作控制")
        control_section_label.setObjectName("sectionLabel")
        right_layout.addWidget(control_section_label)
        
        # 按钮布局
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        # 开始压缩按钮
        self.compress_button = QPushButton("开始压缩")
        self.compress_button.setObjectName("compressButton")
        self.compress_button.setMinimumHeight(45)
        self.compress_button.setEnabled(False)
        button_layout.addWidget(self.compress_button)
        
        # 其他控制按钮
        button_row_layout = QHBoxLayout()
        
        self.preview_button = QPushButton("预览设置")
        self.preview_button.setObjectName("previewButton")
        self.preview_button.setEnabled(False)
        button_row_layout.addWidget(self.preview_button)
        
        self.reset_button = QPushButton("重置设置")
        self.reset_button.setObjectName("resetButton")
        button_row_layout.addWidget(self.reset_button)
        
        button_layout.addLayout(button_row_layout)
        
        right_layout.addLayout(button_layout)
        right_layout.addStretch()
        
        return right_frame
    
    def create_footer_section(self, parent_layout):
        """创建底部状态区域"""
        footer_frame = QFrame()
        footer_frame.setObjectName("footerFrame")
        footer_frame.setFrameStyle(QFrame.StyledPanel)
        footer_frame.setMaximumHeight(80)
        
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        footer_layout.setSpacing(5)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setVisible(False)
        footer_layout.addWidget(self.progress_bar)
        
        # 状态信息
        self.status_info_label = QLabel("就绪")
        self.status_info_label.setObjectName("statusInfoLabel")
        self.status_info_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(self.status_info_label)
        
        parent_layout.addWidget(footer_frame)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 打开文件
        open_action = QAction("打开视频文件", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # 退出应用
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具")
        
        # FFmpeg信息
        ffmpeg_info_action = QAction("FFmpeg信息", self)
        ffmpeg_info_action.triggered.connect(self.show_ffmpeg_info)
        tools_menu.addAction(ffmpeg_info_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        # 关于
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
        """创建状态栏"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # 左侧状态信息
        self.status_label = QLabel("就绪")
        status_bar.addWidget(self.status_label)
        
        # 右侧版本信息
        version_label = QLabel(f"v{self.config['app']['version']}")
        status_bar.addPermanentWidget(version_label)
    
    def load_config(self):
        """加载配置文件"""
        config_path = Path("config.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"配置文件加载失败: {e}")
            # 返回默认配置
            return {
                "app": {
                    "name": "视频压缩器",
                    "version": "1.0.0",
                    "window": {"width": 800, "height": 600, "min_width": 600, "min_height": 400}
                }
            }
    
    def load_styles(self):
        """加载QSS样式"""
        # 使用绝对路径确保样式文件正确加载
        style_path = Path(__file__).parent.parent / "resources" / "styles" / "main.qss"
        print(f"尝试加载样式文件: {style_path}")
        print(f"样式文件是否存在: {style_path.exists()}")
        
        if style_path.exists():
            try:
                with open(style_path, 'r', encoding='utf-8') as f:
                    style_content = f.read()
                    self.setStyleSheet(style_content)
                    print("QSS样式加载成功")
            except Exception as e:
                print(f"样式文件加载失败: {e}")
                self.apply_default_styles()
        else:
            print("样式文件不存在，使用默认样式")
            self.apply_default_styles()
    
    def apply_default_styles(self):
        """应用默认样式"""
        default_style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        #headerFrame, #leftPanel, #rightPanel, #footerFrame,
        #fileDropArea, #videoInfoFrame, #compressionSettingsFrame {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
        
        #titleLabel {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        #subtitleLabel {
            font-size: 14px;
            color: #7f8c8d;
        }
        
        #sectionLabel {
            font-size: 16px;
            font-weight: bold;
            color: #34495e;
            margin-bottom: 10px;
        }
        
        #compressButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
        }
        
        #compressButton:hover {
            background-color: #2980b9;
        }
        
        #compressButton:disabled {
            background-color: #bdc3c7;
        }
        
        #previewButton, #resetButton {
            background-color: #95a5a6;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
        }
        
        #previewButton:hover, #resetButton:hover {
            background-color: #7f8c8d;
        }
        
        #dropInfoLabel, #settingsInfoLabel {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        #ffmpegStatus {
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 4px;
        }
        
        #progressBar {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            text-align: center;
        }
        
        #progressBar::chunk {
            background-color: #3498db;
            border-radius: 3px;
        }
        """
        self.setStyleSheet(default_style)
    
    def connect_signals(self):
        """连接信号和槽"""
        # 按钮信号连接（暂时为空实现）
        self.compress_button.clicked.connect(self.start_compression)
        self.preview_button.clicked.connect(self.preview_settings)
        self.reset_button.clicked.connect(self.reset_settings)
    
    def check_ffmpeg_status(self):
        """检查FFmpeg状态"""
        # 导入FFmpeg管理器并检查状态
        try:
            from app.core.ffmpeg_manager import ffmpeg_manager
            self.ffmpeg_manager = ffmpeg_manager
            # 异步检查FFmpeg状态
            QTimer.singleShot(500, self.update_ffmpeg_status)
        except ImportError as e:
            print(f"FFmpeg管理器导入失败: {e}")
            self.ffmpeg_status_label.setText("FFmpeg: 检查失败")
    
    def update_ffmpeg_status(self):
        """更新FFmpeg状态显示"""
        try:
            ffmpeg_info = self.ffmpeg_manager.get_ffmpeg_info()
            if ffmpeg_info["available"]:
                self.ffmpeg_status_label.setText("FFmpeg: 已安装 ✓")
                self.ffmpeg_status_label.setStyleSheet("""
                    QPushButton#ffmpegStatus {
                        background-color: #28a745; 
                        color: white; 
                        padding: 6px 12px; 
                        border-radius: 4px;
                        border: none;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton#ffmpegStatus:hover {
                        background-color: #218838;
                    }
                """)
                self.ffmpeg_status_label.setToolTip(f"FFmpeg已安装: {ffmpeg_info['path']}")
                print(f"FFmpeg可用: {ffmpeg_info['path']}")
            else:
                self.ffmpeg_status_label.setText("FFmpeg: 未安装 ⚠️")
                self.ffmpeg_status_label.setStyleSheet("""
                    QPushButton#ffmpegStatus {
                        background-color: #dc3545; 
                        color: white; 
                        padding: 6px 12px; 
                        border-radius: 4px;
                        border: none;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton#ffmpegStatus:hover {
                        background-color: #c82333;
                    }
                """)
                self.ffmpeg_status_label.setToolTip("点击安装FFmpeg")
                print("FFmpeg不可用")
        except Exception as e:
            print(f"FFmpeg状态检查错误: {e}")
            self.ffmpeg_status_label.setText("FFmpeg: 检查失败")
            self.ffmpeg_status_label.setStyleSheet("""
                QPushButton#ffmpegStatus {
                    background-color: #ffc107; 
                    color: black; 
                    padding: 6px 12px; 
                    border-radius: 4px;
                    border: none;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton#ffmpegStatus:hover {
                    background-color: #e0a800;
                }
            """)
            self.ffmpeg_status_label.setToolTip("FFmpeg状态检查失败，点击重试")
    
    def on_file_selected(self, file_path: str):
        """处理文件选择事件"""
        print(f"选择的文件: {file_path}")
        self.current_video_file = file_path
        
        # 启用压缩按钮
        self.compress_button.setEnabled(True)
        self.preview_button.setEnabled(True)
        
        # 更新视频信息显示
        self.update_video_info(file_path)
        
        # 更新状态
        self.show_message(f"已选择文件: {Path(file_path).name}")
    
    def update_video_info(self, file_path: str):
        """更新视频信息显示"""
        try:
            import os
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            file_name = Path(file_path).name
            
            # 为小窗口优化的紧凑显示格式
            info_text = f"""<div style='padding: 8px; line-height: 1.3;'>
<div style='text-align: center; margin-bottom: 8px;'>
<p style='font-weight: bold; font-size: 14px; color: #2c3e50; margin: 0 0 6px 0;'>文件名: {file_name}</p>
<p style='font-size: 12px; color: #34495e; margin: 0 0 6px 0;'>文件大小: {file_size:.1f} MB</p>
</div>
<div style='background-color: #f8f9fa; padding: 6px; border-radius: 4px; margin-bottom: 6px;'>
<p style='font-size: 10px; color: #6c757d; margin: 0; word-wrap: break-word; text-align: center;'>
<strong>路径:</strong><br/>{file_path}
</p>
</div>
<div style='text-align: center;'>
<p style='font-size: 11px; color: #007bff; margin: 0;'>📊 正在获取视频详细信息...</p>
</div>
</div>"""
            
            self.video_info_label.setText(info_text)
            
        except Exception as e:
            self.video_info_label.setText(f"""<div style='text-align: center; color: #dc3545; padding: 15px;'>
<p style='font-size: 12px; margin: 0;'>⚠️ 无法获取文件信息</p>
<p style='font-size: 10px; margin: 4px 0 0 0;'>{e}</p>
</div>""")
    
    def open_file_dialog(self):
        """打开文件对话框"""
        # 直接调用文件拖拽组件的文件选择功能
        if hasattr(self, 'file_drop_area'):
            self.file_drop_area.open_file_dialog()
    
    def start_compression(self):
        """开始压缩"""
        # 检查前置条件
        if not hasattr(self, 'current_video_file') or not self.current_video_file:
            self.show_message("请先选择视频文件")
            return
            
        if not hasattr(self, 'current_compression_settings') or not self.current_compression_settings:
            self.show_message("请配置压缩设置")
            return
        
        # 检查FFmpeg是否可用
        ffmpeg_info = self.ffmpeg_manager.get_ffmpeg_info()
        if not ffmpeg_info["available"]:
            self.show_message("FFmpeg未安装，请先安装FFmpeg")
            return
        
        # 如果已有压缩任务在运行，先停止
        if self.compression_thread and self.compression_thread.isRunning():
            self.stop_compression()
            return
        
        # 生成输出文件路径
        input_path = Path(self.current_video_file)
        output_dir = Path(self.config['compression']['output_directory'])
        output_dir.mkdir(exist_ok=True)
        
        # 生成唯一的输出文件名
        timestamp = int(time.time())
        output_filename = f"{input_path.stem}_compressed_{timestamp}.mp4"
        output_path = output_dir / output_filename
        
        # 创建并配置压缩线程
        from app.core.compression_thread import CompressionThread
        self.compression_thread = CompressionThread(self)
        self.compression_thread.setup_compression(
            str(input_path),
            str(output_path), 
            self.current_compression_settings
        )
        
        # 连接信号
        self.compression_thread.progress_updated.connect(self.on_compression_progress)
        self.compression_thread.compression_finished.connect(self.on_compression_finished)
        self.compression_thread.compression_error.connect(self.on_compression_error)
        
        # 更新UI状态
        self.compress_button.setText("取消压缩")
        self.compress_button.setObjectName("cancelButton")
        self.compress_button.setStyleSheet("""
            QPushButton#cancelButton {
                background-color: #dc3545;
                color: white;
                font-size: 14px;
                min-height: 40px;
            }
            QPushButton#cancelButton:hover {
                background-color: #c82333;
            }
        """)
        self.preview_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 启动压缩线程
        self.compression_thread.start()
        self.show_message(f"开始压缩: {input_path.name}")
    
    def preview_settings(self):
        """预览设置"""
        # 占位符实现
        self.show_message("预览功能将在后续实现")
    
    def reset_settings(self):
        """重置设置"""
        if hasattr(self, 'compression_settings'):
            self.compression_settings.reset_to_defaults()
            self.show_message("设置已重置为默认值")
    
    def stop_compression(self):
        """停止压缩任务"""
        if self.compression_thread and self.compression_thread.isRunning():
            self.compression_thread.stop_compression()
            self.show_message("正在取消压缩...")
            
    def on_compression_progress(self, progress: int, status: str):
        """处理压缩进度更新"""
        if progress >= 0:
            self.progress_bar.setValue(progress)
        self.status_info_label.setText(status)
        
    def on_compression_finished(self, success: bool, message: str, output_file_path: str = ""):
        """处理压缩完成"""
        # 重置UI状态
        self.reset_compression_ui()
        
        if success and output_file_path:
            # 显示成功消息
            self.show_message(f"✅ {message}")
            
            # 显示详细的完成对话框
            self.show_compression_success_dialog(output_file_path)
        else:
            self.show_message(f"❌ 压缩失败: {message}")
    
    def show_compression_success_dialog(self, output_file_path: str):
        """显示压缩成功的详细对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
        from PyQt5.QtCore import Qt
        import subprocess
        import platform
        
        dialog = QDialog(self)
        dialog.setWindowTitle("压缩完成")
        dialog.setFixedSize(500, 300)
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # 成功图标和标题
        title_layout = QHBoxLayout()
        title_label = QLabel("🎉 视频压缩成功！")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #28a745; margin: 10px 0;")
        title_layout.addWidget(title_label)
        layout.addLayout(title_layout)
        
        # 文件信息
        output_path = Path(output_file_path)
        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        
        info_text = f"""
文件名: {output_path.name}
文件大小: {file_size:.1f} MB
保存位置: {output_path.parent}

完整路径:
{output_file_path}
        """.strip()
        
        info_area = QTextEdit()
        info_area.setPlainText(info_text)
        info_area.setReadOnly(True)
        info_area.setMaximumHeight(120)
        info_area.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px;
                font-family: monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(info_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 打开文件夹按钮
        open_folder_btn = QPushButton("📁 打开文件夹")
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        def open_output_folder():
            """打开输出文件夹"""
            try:
                folder_path = str(output_path.parent)
                
                # 跨平台打开文件夹
                if platform.system() == "Windows":
                    subprocess.run(["explorer", folder_path])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", folder_path])
                else:  # Linux
                    subprocess.run(["xdg-open", folder_path])
                    
                dialog.accept()
                
            except Exception as e:
                QMessageBox.warning(dialog, "错误", f"无法打开文件夹: {e}")
        
        open_folder_btn.clicked.connect(open_output_folder)
        button_layout.addWidget(open_folder_btn)
        
        # 复制路径按钮
        copy_path_btn = QPushButton("📋 复制路径")
        copy_path_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        
        def copy_file_path():
            """复制文件路径到剪贴板"""
            try:
                from PyQt5.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(output_file_path)
                copy_path_btn.setText("✅ 已复制")
                QTimer.singleShot(2000, lambda: copy_path_btn.setText("📋 复制路径"))
            except Exception as e:
                QMessageBox.warning(dialog, "错误", f"无法复制路径: {e}")
        
        copy_path_btn.clicked.connect(copy_file_path)
        button_layout.addWidget(copy_path_btn)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # 显示对话框
        dialog.exec_()
    
    def on_compression_error(self, error_message: str):
        """处理压缩错误"""
        self.reset_compression_ui()
        self.show_message(f"❌ 错误: {error_message}")
        
        # 显示详细错误对话框
        QMessageBox.critical(self, "压缩错误", f"压缩过程中发生错误:\n\n{error_message}")
    
    def reset_compression_ui(self):
        """重置压缩相关的UI状态"""
        # 重置按钮
        self.compress_button.setText("开始压缩")
        self.compress_button.setObjectName("compressButton")
        self.compress_button.setStyleSheet("")  # 使用默认样式
        
        # 启用其他按钮
        self.preview_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        
        # 清理线程
        if self.compression_thread:
            self.compression_thread.deleteLater()
            self.compression_thread = None

    def on_compression_settings_changed(self, settings: dict):
        """处理压缩设置变化"""
        self.current_compression_settings = settings
        print(f"压缩设置已更新: {settings.get('preset', 'unknown')}")
        
        # 如果有文件选择且设置有效，启用压缩按钮
        if hasattr(self, 'current_video_file') and settings:
            self.compress_button.setEnabled(True)
    
    def show_ffmpeg_info(self):
        """显示FFmpeg安装对话框"""
        from app.widgets.ffmpeg_install_dialog import FFmpegInstallDialog
        dialog = FFmpegInstallDialog(self)
        dialog.exec_()
        
        # 安装完成后刷新状态
        self.check_ffmpeg_status()
    
    def show_about_dialog(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            f"{self.config['app']['name']} v{self.config['app']['version']}\n\n"
            "一个简单易用的视频压缩工具\n"
            "基于Python和PyQt6开发"
        )
    
    def show_message(self, message: str):
        """显示消息"""
        self.status_label.setText(message)
        self.status_info_label.setText(message)
        QTimer.singleShot(3000, lambda: self.status_label.setText("就绪"))
        QTimer.singleShot(3000, lambda: self.status_info_label.setText("就绪"))
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 确认退出
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出视频压缩器吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 如果有正在进行的压缩任务，先停止
            if self.compression_thread and self.compression_thread.isRunning():
                self.compression_thread.terminate()
                self.compression_thread.wait()
            
            event.accept()
        else:
            event.ignore() 