#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件拖拽组件 - 支持拖拽上传和点击选择视频文件
"""

import os
from pathlib import Path
from typing import List, Optional

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent


class FileDropWidget(QFrame):
    """文件拖拽组件"""
    
    # 信号定义
    file_selected = pyqtSignal(str)  # 文件被选择时发射，传递文件路径
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 支持的视频格式
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.3gp', '.webm']
        
        # 设置组件属性
        self.setup_widget()
        
        # 创建UI
        self.setup_ui()
    
    def setup_widget(self):
        """设置组件属性"""
        self.setObjectName("fileDropArea")
        self.setAcceptDrops(True)  # 启用拖拽接受
        self.setMinimumHeight(160)  # 按3:2比例增加高度
        self.setMaximumHeight(240)  # 按比例调整最大高度
        
        # 设置鼠标追踪，用于悬停效果
        self.setMouseTracking(True)
    
    def setup_ui(self):
        """创建用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 拖拽图标和提示文本
        self.drop_label = QLabel("📁 拖拽视频文件到此处")
        self.drop_label.setObjectName("dropInfoLabel")
        self.drop_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.drop_label)
        
        # 或者分割线
        or_label = QLabel("或者")
        or_label.setAlignment(Qt.AlignCenter)
        or_label.setStyleSheet("color: #999; font-size: 12px;")
        layout.addWidget(or_label)
        
        # 选择文件按钮
        self.select_button = QPushButton("点击选择文件")
        self.select_button.setObjectName("selectFileButton")
        self.select_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.select_button)
        
        # 支持格式提示
        format_text = "支持格式: " + ", ".join(self.supported_formats)
        self.format_label = QLabel(format_text)
        self.format_label.setAlignment(Qt.AlignCenter)
        self.format_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.format_label)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否有有效的视频文件
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if self.is_supported_video_file(file_path):
                    event.acceptProposedAction()
                    self.set_drag_hover_style(True)
                    return
        
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.set_drag_hover_style(False)
        super().dragLeaveEvent(event)
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        self.set_drag_hover_style(False)
        
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()  # 只处理第一个文件
            if self.is_supported_video_file(file_path):
                self.handle_file_selection(file_path)
                event.acceptProposedAction()
            else:
                self.show_error_message("不支持的文件格式", 
                                      f"请选择支持的视频格式: {', '.join(self.supported_formats)}")
        
        event.ignore()
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.open_file_dialog()
        super().mousePressEvent(event)
    
    def open_file_dialog(self):
        """打开文件选择对话框"""
        # 构建文件过滤器
        filter_text = "视频文件 ("
        for fmt in self.supported_formats:
            filter_text += f"*{fmt} "
        filter_text = filter_text.strip() + ");;所有文件 (*)"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            str(Path.home()),
            filter_text
        )
        
        if file_path:
            self.handle_file_selection(file_path)
    
    def handle_file_selection(self, file_path: str):
        """处理文件选择"""
        if not os.path.exists(file_path):
            self.show_error_message("文件不存在", f"选择的文件不存在: {file_path}")
            return
        
        if not self.is_supported_video_file(file_path):
            self.show_error_message("不支持的格式", 
                                  f"请选择支持的视频格式: {', '.join(self.supported_formats)}")
            return
        
        # 检查文件大小（可选限制）
        file_size = os.path.getsize(file_path)
        max_size = 2 * 1024 * 1024 * 1024  # 2GB
        if file_size > max_size:
            self.show_error_message("文件过大", 
                                  f"文件大小超过限制 (2GB)，当前文件: {file_size / (1024*1024*1024):.1f}GB")
            return
        
        # 更新界面显示
        self.update_selected_file_display(file_path)
        
        # 发射信号
        self.file_selected.emit(file_path)
    
    def is_supported_video_file(self, file_path: str) -> bool:
        """检查是否为支持的视频文件"""
        if not file_path:
            return False
        
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.supported_formats
    
    def update_selected_file_display(self, file_path: str):
        """更新选中文件的显示"""
        file_name = Path(file_path).name
        self.drop_label.setText(f"✅ 已选择: {file_name}")
        self.select_button.setText("重新选择文件")
    
    def reset_display(self):
        """重置显示为初始状态"""
        self.drop_label.setText("📁 拖拽视频文件到此处")
        self.select_button.setText("点击选择文件")
    
    def set_drag_hover_style(self, hover: bool):
        """设置拖拽悬停样式"""
        if hover:
            self.setStyleSheet("""
                #fileDropArea {
                    border: 2px solid #007bff;
                    background-color: #e3f2fd;
                }
            """)
        else:
            self.setStyleSheet("")  # 恢复默认样式
    
    def show_error_message(self, title: str, message: str):
        """显示错误消息"""
        QMessageBox.warning(self, title, message)
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的格式列表"""
        return self.supported_formats.copy()
    
    def set_supported_formats(self, formats: List[str]):
        """设置支持的格式"""
        self.supported_formats = [fmt.lower() for fmt in formats]
        format_text = "支持格式: " + ", ".join(self.supported_formats)
        self.format_label.setText(format_text) 