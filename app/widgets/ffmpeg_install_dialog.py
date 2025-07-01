#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg安装对话框 - 提供FFmpeg下载和安装功能
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QProgressBar, QTextEdit, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from typing import Optional

from app.core.ffmpeg_installer import FFmpegInstaller


class FFmpegInstallWorker(QThread):
    """FFmpeg安装工作线程"""
    
    progress_updated = pyqtSignal(int, str)  # 进度百分比, 状态消息
    installation_finished = pyqtSignal(bool, str)  # 是否成功, 消息
    
    def __init__(self):
        super().__init__()
        self.installer = FFmpegInstaller()
    
    def run(self):
        """执行安装"""
        try:
            def progress_callback(percentage, message):
                self.progress_updated.emit(percentage, message)
            
            success, message = self.installer.install_ffmpeg(progress_callback)
            self.installation_finished.emit(success, message)
            
        except Exception as e:
            self.installation_finished.emit(False, f"安装过程中发生错误: {str(e)}")


class FFmpegInstallDialog(QDialog):
    """FFmpeg安装对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.installer = FFmpegInstaller()
        self.install_worker: Optional[FFmpegInstallWorker] = None
        
        self.setup_dialog()
        self.setup_ui()
        self.check_current_status()
    
    def setup_dialog(self):
        """设置对话框属性"""
        self.setWindowTitle("FFmpeg 安装器")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        # 设置对话框居中
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)
    
    def setup_ui(self):
        """创建用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("FFmpeg 视频处理工具")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 状态信息框
        self.status_frame = QFrame()
        self.status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QVBoxLayout(self.status_frame)
        
        self.status_label = QLabel("正在检查 FFmpeg 状态...")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(self.status_frame)
        
        # 系统信息
        info_label = QLabel(f"系统: {self.installer.system.title()} ({self.installer.architecture})")
        info_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(info_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 进度信息
        self.progress_label = QLabel()
        self.progress_label.setVisible(False)
        self.progress_label.setStyleSheet("color: #007bff; font-size: 12px;")
        layout.addWidget(self.progress_label)
        
        # 详细日志（可选）
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)
        self.log_text.setVisible(False)
        layout.addWidget(self.log_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.install_button = QPushButton("安装 FFmpeg")
        self.install_button.setMinimumHeight(35)
        self.install_button.clicked.connect(self.start_installation)
        button_layout.addWidget(self.install_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # 显示详细信息按钮
        self.details_button = QPushButton("显示详细信息")
        self.details_button.clicked.connect(self.toggle_details)
        layout.addWidget(self.details_button)
    
    def check_current_status(self):
        """检查当前FFmpeg状态"""
        QTimer.singleShot(100, self._do_status_check)
    
    def _do_status_check(self):
        """执行状态检查"""
        try:
            installed, path = self.installer.is_ffmpeg_installed()
            
            if installed:
                self.status_label.setText(f"""✅ FFmpeg 已安装
                
路径: {path}
状态: 可以正常使用

FFmpeg 已经可用，您可以直接开始使用视频压缩功能。""")
                self.status_frame.setStyleSheet("background-color: #d4edda; border: 1px solid #c3e6cb;")
                self.install_button.setText("重新安装")
                self.install_button.setStyleSheet("background-color: #6c757d;")
            else:
                self.status_label.setText(f"""❌ 未检测到 FFmpeg
                
FFmpeg 是视频处理的核心工具，需要安装后才能使用压缩功能。

本程序将自动下载适合您系统的 FFmpeg 版本。""")
                self.status_frame.setStyleSheet("background-color: #f8d7da; border: 1px solid #f5c6cb;")
                self.install_button.setText("开始安装")
                self.install_button.setStyleSheet("background-color: #007bff; color: white;")
        
        except Exception as e:
            self.status_label.setText(f"检查状态时出错: {e}")
            self.status_frame.setStyleSheet("background-color: #fff3cd; border: 1px solid #ffeaa7;")
    
    def start_installation(self):
        """开始安装FFmpeg"""
        if self.install_worker and self.install_worker.isRunning():
            return
        
        # 确认安装
        reply = QMessageBox.question(
            self, 
            "确认安装", 
            "是否开始下载并安装 FFmpeg？\n\n下载大小约为 50-100MB，具体取决于您的系统平台。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # 准备UI
        self.install_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)
        self.progress_label.setText("准备下载...")
        
        # 显示日志
        self.log_text.setVisible(True)
        self.log_text.clear()
        self.log_text.append("开始 FFmpeg 安装过程...")
        
        # 启动安装线程
        self.install_worker = FFmpegInstallWorker()
        self.install_worker.progress_updated.connect(self.update_progress)
        self.install_worker.installation_finished.connect(self.installation_completed)
        self.install_worker.start()
    
    def update_progress(self, percentage: int, message: str):
        """更新安装进度"""
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(message)
        self.log_text.append(f"[{percentage}%] {message}")
        
        # 滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def installation_completed(self, success: bool, message: str):
        """安装完成"""
        self.install_button.setEnabled(True)
        
        if success:
            self.progress_bar.setValue(100)
            self.progress_label.setText("安装完成！")
            self.log_text.append(f"✅ {message}")
            
            # 更新状态显示
            self.check_current_status()
            
            # 显示成功消息
            QMessageBox.information(
                self,
                "安装成功",
                "FFmpeg 安装成功！\n\n现在您可以开始使用视频压缩功能了。"
            )
            
        else:
            self.progress_label.setText("安装失败")
            self.log_text.append(f"❌ {message}")
            
            # 显示错误消息
            QMessageBox.critical(
                self,
                "安装失败",
                f"FFmpeg 安装失败：\n\n{message}\n\n请检查网络连接后重试。"
            )
    
    def toggle_details(self):
        """切换详细信息显示"""
        if self.log_text.isVisible():
            self.log_text.setVisible(False)
            self.details_button.setText("显示详细信息")
            self.resize(500, 300)
        else:
            self.log_text.setVisible(True)
            self.details_button.setText("隐藏详细信息")
            self.resize(500, 450)
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.install_worker and self.install_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认关闭",
                "安装正在进行中，确定要关闭吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.install_worker.terminate()
                self.install_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept() 