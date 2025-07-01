#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频压缩后台线程 - 使用QThread在后台执行压缩任务
"""

from PyQt5.QtCore import QThread, pyqtSignal
from typing import Dict, Any
from pathlib import Path
from app.core.video_compressor import video_compressor


class CompressionThread(QThread):
    """视频压缩后台线程"""
    
    # 信号定义
    progress_updated = pyqtSignal(int, str)  # 进度百分比, 状态消息
    compression_finished = pyqtSignal(bool, str, str)  # 是否成功, 结果消息, 输出文件路径
    compression_error = pyqtSignal(str)  # 错误消息
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_file = ""
        self.output_file = ""
        self.settings = {}
        self.is_running = False
        
    def setup_compression(self, input_file: str, output_file: str, settings: Dict[str, Any]):
        """设置压缩任务参数"""
        self.input_file = input_file
        self.output_file = output_file
        self.settings = settings.copy()
        
    def run(self):
        """执行压缩任务"""
        try:
            self.is_running = True
            
            # 检查参数
            if not self.input_file or not self.output_file:
                self.compression_error.emit("压缩参数不完整")
                return
            
            # 生成输出文件名
            if not self.output_file.endswith('.mp4'):
                self.output_file = str(Path(self.output_file).with_suffix('.mp4'))
            
            # 执行压缩
            success = video_compressor.compress_video(
                input_file=self.input_file,
                output_file=self.output_file,
                settings=self.settings,
                progress_callback=self._on_progress,
                error_callback=self._on_error
            )
            
            # 发出完成信号
            if success:
                # 检查输出文件是否存在
                output_path = Path(self.output_file)
                if output_path.exists():
                    file_size = output_path.stat().st_size / (1024 * 1024)  # MB
                    message = f"压缩完成！输出文件: {output_path.name} ({file_size:.1f} MB)"
                    self.compression_finished.emit(True, message, str(output_path))
                else:
                    self.compression_finished.emit(False, "压缩完成但输出文件不存在", "")
            else:
                self.compression_finished.emit(False, "压缩失败", "")
                
        except Exception as e:
            self.compression_error.emit(f"压缩线程执行错误: {str(e)}")
        finally:
            self.is_running = False
    
    def _on_progress(self, progress: int, status: str):
        """进度回调"""
        if progress is not None:
            self.progress_updated.emit(progress, status)
        else:
            # 如果进度为None，只更新状态消息，保持当前进度
            self.progress_updated.emit(-1, status)
    
    def _on_error(self, error_message: str):
        """错误回调"""
        self.compression_error.emit(error_message)
    
    def stop_compression(self):
        """停止压缩任务"""
        if self.is_running:
            video_compressor.cancel_compression()
            self.requestInterruption()
            self.wait(5000)  # 等待最多5秒
            if self.isRunning():
                self.terminate()  # 强制终止
    
    def get_estimated_output_size(self) -> int:
        """获取估算的输出文件大小"""
        if self.input_file and self.settings:
            return video_compressor.get_estimated_output_size(self.input_file, self.settings)
        return 0 