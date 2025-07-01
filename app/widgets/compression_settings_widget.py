#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压缩设置组件 - 提供预设选择和自定义压缩参数设置
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QCheckBox, QSlider, QSpinBox, 
                             QGroupBox, QGridLayout, QFrame, QButtonGroup,
                             QRadioButton, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from app.core.compression_presets import compression_presets


class CompressionSettingsWidget(QWidget):
    """压缩设置组件"""
    
    # 信号：当设置发生变化时发出
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_preset = "standard"  # 默认预设
        self.current_settings = {}
        self.setup_ui()
        self.load_preset("standard")
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建滚动区域以适应小窗口
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 应用样式
        self.apply_modern_styles()
        
        # 1. 预设选择区域
        self.create_preset_section(layout)
        
        # 2. 质量设置区域
        self.create_quality_section(layout)
        
        # 3. 分辨率和帧率设置
        self.create_resolution_section(layout)
        
        # 4. 音频设置区域
        self.create_audio_section(layout)
        
        # 5. 高级设置区域（可折叠）
        self.create_advanced_section(layout)
        
        layout.addStretch()
        
    def apply_modern_styles(self):
        """应用现代化样式"""
        self.setStyleSheet("""
            /* 主容器样式 */
            QWidget {
                background-color: #ffffff;
                color: #2c3e50;
            }
            
            /* 滚动区域样式 */
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            
            /* 分组框样式 */
            QGroupBox {
                font-size: 15px;
                font-weight: 600;
                color: #2c3e50;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                margin: 8px 0px;
                padding: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ffffff, stop:1 #f8f9fa);
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 4px 12px;
                background-color: #ffffff;
                border: 2px solid #007bff;
                border-radius: 8px;
                color: #007bff;
                font-weight: bold;
            }
            
            /* 下拉框样式 */
            QComboBox {
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 10px 15px;
                background-color: #ffffff;
                font-size: 13px;
                min-height: 25px;
                color: #495057;
                selection-background-color: #007bff;
            }
            
            QComboBox:hover {
                border-color: #007bff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #f8f9ff, stop:1 #e3f2fd);
            }
            
            QComboBox:focus {
                border-color: #007bff;
                background-color: #ffffff;
                outline: none;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: none;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            
            QComboBox::drop-down:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #007bff, stop:1 #0056b3);
            }
            
            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #6c757d;
                margin: 2px;
            }
            
            QComboBox::down-arrow:hover {
                border-top-color: #ffffff;
            }
            
            /* 下拉框展开列表样式 */
            QComboBox QAbstractItemView {
                border: 2px solid #007bff;
                border-radius: 8px;
                background-color: #ffffff;
                selection-background-color: #e3f2fd;
                selection-color: #1976d2;
                padding: 4px;
            }
            
            QComboBox QAbstractItemView::item {
                height: 35px;
                padding: 8px 12px;
                margin: 2px;
                border-radius: 6px;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #007bff;
                color: white;
            }
            
            /* 预设组合框特殊样式 */
            QComboBox#presetCombo {
                font-size: 14px;
                font-weight: 600;
                min-height: 30px;
                padding: 12px 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ffffff, stop:1 #f1f3f4);
                border: 2px solid #007bff;
                color: #1976d2;
            }
            
            QComboBox#presetCombo:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #e3f2fd, stop:1 #bbdefb);
            }
            
            /* 标签样式 */
            QLabel {
                color: #495057;
                font-size: 13px;
                font-weight: 500;
            }
            
            QLabel#presetDescription {
                color: #6c757d;
                font-size: 12px;
                font-weight: normal;
                font-style: italic;
                background-color: #f8f9fa;
                padding: 12px 16px;
                border-radius: 8px;
                border-left: 4px solid #17a2b8;
                margin: 8px 0px;
                line-height: 1.4;
            }
            
            /* 滑块样式 */
            QSlider::groove:horizontal {
                border: none;
                height: 8px;
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #28a745, stop:0.5 #ffc107, stop:1 #dc3545);
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ffffff, stop:1 #007bff);
                border: 3px solid #007bff;
                width: 20px;
                margin: -8px 0;
                border-radius: 13px;
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ffffff, stop:1 #0056b3);
                border-color: #0056b3;
                width: 22px;
                margin: -9px 0;
                border-radius: 14px;
            }
            
            QSlider::handle:horizontal:pressed {
                background: #007bff;
                border-color: #004085;
            }
            
            /* 现代化复选框样式 */
            QCheckBox {
                font-size: 15px;
                font-weight: 600;
                color: #495057;
                spacing: 12px;
                padding: 4px;
            }
            
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background-color: #ffffff;
            }
            
            QCheckBox::indicator:hover {
                border-color: #007bff;
                background-color: #f8f9ff;
            }
            
            QCheckBox::indicator:checked {
                background-color: #007bff;
                border-color: #007bff;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNC42NjY2N0w2IDEyTDIuNjY2NjcgOC42NjY2NyIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
            
            QCheckBox::indicator:checked:hover {
                background-color: #0056b3;
                border-color: #0056b3;
            }
            
            /* 框架样式 */
            QFrame {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background-color: #f8f9fa;
                padding: 8px;
                margin: 4px 0px;
            }
        """)
        
    def create_preset_section(self, parent_layout):
        """创建预设选择区域"""
        preset_group = QGroupBox("🎯 压缩预设")
        preset_group.setObjectName("presetGroup")
        preset_layout = QVBoxLayout(preset_group)
        preset_layout.setSpacing(16)
        
        # 预设选择容器
        preset_container = QFrame()
        preset_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #e3f2fd, stop:1 #f3e5f5);
                border: 2px solid #007bff;
                border-radius: 12px;
                padding: 16px;
                margin: 4px;
            }
        """)
        
        preset_container_layout = QVBoxLayout(preset_container)
        preset_container_layout.setSpacing(12)
        
        # 预设标题
        preset_title = QLabel("选择压缩预设")
        preset_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1976d2;
                margin: 0px;
                padding: 0px;
            }
        """)
        preset_container_layout.addWidget(preset_title)
        
        # 预设选择下拉框
        self.preset_combo = QComboBox()
        self.preset_combo.setObjectName("presetCombo")
        
        presets = compression_presets.get_all_presets()
        for preset_key, preset_data in presets.items():
            display_text = f"{preset_data['icon']} {preset_data['name']} - {preset_data['compression_ratio']}"
            self.preset_combo.addItem(display_text, preset_key)
        
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_container_layout.addWidget(self.preset_combo)
        
        preset_layout.addWidget(preset_container)
        
        # 预设描述标签
        self.preset_description = QLabel()
        self.preset_description.setObjectName("presetDescription")
        self.preset_description.setWordWrap(True)
        preset_layout.addWidget(self.preset_description)
        
        parent_layout.addWidget(preset_group)
        
    def create_quality_section(self, parent_layout):
        """创建质量设置区域"""
        quality_group = QGroupBox("🎛️ 质量设置")
        quality_layout = QGridLayout(quality_group)
        quality_layout.setSpacing(12)
        
        # CRF质量滑块
        quality_label = QLabel("视频质量:")
        quality_label.setStyleSheet("font-weight: 600; color: #495057;")
        quality_layout.addWidget(quality_label, 0, 0)
        
        self.crf_slider = QSlider(Qt.Horizontal)
        self.crf_slider.setRange(15, 35)
        self.crf_slider.setValue(23)
        self.crf_slider.setTickPosition(QSlider.TicksBelow)
        self.crf_slider.setTickInterval(5)
        self.crf_slider.valueChanged.connect(self.on_settings_changed)
        quality_layout.addWidget(self.crf_slider, 0, 1)
        
        self.crf_label = QLabel("23 (标准)")
        self.crf_label.setMinimumWidth(80)
        self.crf_label.setStyleSheet("""
            background-color: #007bff;
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: bold;
            text-align: center;
        """)
        quality_layout.addWidget(self.crf_label, 0, 2)
        
        # 质量说明
        quality_hint = QLabel("← 较低数值 = 更高质量  |  较高数值 = 更小文件 →")
        quality_hint.setStyleSheet("""
            color: #6c757d;
            font-size: 11px;
            font-style: italic;
            text-align: center;
            margin: 4px 0px;
        """)
        quality_layout.addWidget(quality_hint, 1, 0, 1, 3)
        
        # 连接CRF滑块值变化
        self.crf_slider.valueChanged.connect(self.update_crf_label)
        
        parent_layout.addWidget(quality_group)
        
    def create_resolution_section(self, parent_layout):
        """创建分辨率和帧率设置区域"""
        res_group = QGroupBox("📐 分辨率与帧率")
        res_layout = QGridLayout(res_group)
        res_layout.setSpacing(12)
        
        # 分辨率选择
        res_label = QLabel("分辨率:")
        res_label.setStyleSheet("font-weight: 600; color: #495057;")
        res_layout.addWidget(res_label, 0, 0)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.setStyleSheet("""
            QComboBox {
                min-height: 28px;
                font-size: 13px;
            }
        """)
        resolutions = compression_presets.RESOLUTION_PRESETS
        for res_key, res_data in resolutions.items():
            self.resolution_combo.addItem(res_data["name"], res_key)
        self.resolution_combo.currentTextChanged.connect(self.on_settings_changed)
        res_layout.addWidget(self.resolution_combo, 0, 1, 1, 2)
        
        # 帧率选择
        fps_label = QLabel("帧率:")
        fps_label.setStyleSheet("font-weight: 600; color: #495057;")
        res_layout.addWidget(fps_label, 1, 0)
        
        self.framerate_combo = QComboBox()
        self.framerate_combo.setStyleSheet("""
            QComboBox {
                min-height: 28px;
                font-size: 13px;
            }
        """)
        framerates = compression_presets.FRAMERATE_PRESETS
        for fps_key, fps_data in framerates.items():
            self.framerate_combo.addItem(fps_data["name"], fps_key)
        self.framerate_combo.currentTextChanged.connect(self.on_settings_changed)
        res_layout.addWidget(self.framerate_combo, 1, 1, 1, 2)
        
        # 提示信息
        res_hint = QLabel("💡 选择较低分辨率和帧率可以显著减小文件大小")
        res_hint.setStyleSheet("""
            color: #6c757d;
            font-size: 11px;
            font-style: italic;
            background-color: #fff3cd;
            padding: 6px 10px;
            border-radius: 4px;
            border-left: 3px solid #ffc107;
            margin: 4px 0px;
        """)
        res_layout.addWidget(res_hint, 2, 0, 1, 3)
        
        parent_layout.addWidget(res_group)
        
    def create_audio_section(self, parent_layout):
        """创建音频设置区域"""
        audio_group = QGroupBox("🔊 音频设置")
        audio_layout = QVBoxLayout(audio_group)
        audio_layout.setSpacing(12)
        
        # 保留音频选项
        self.keep_audio_checkbox = QCheckBox("🎵 保留音频")
        self.keep_audio_checkbox.setChecked(True)
        self.keep_audio_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 15px;
                font-weight: 600;
                color: #495057;
                spacing: 10px;
                padding: 8px;
                background-color: #e8f5e8;
                border-radius: 6px;
                border: 1px solid #28a745;
            }
            QCheckBox:hover {
                background-color: #d4edd4;
            }
        """)
        self.keep_audio_checkbox.stateChanged.connect(self.on_audio_settings_changed)
        audio_layout.addWidget(self.keep_audio_checkbox)
        
        # 音频质量设置（当保留音频时显示）
        self.audio_settings_frame = QFrame()
        self.audio_settings_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;
                margin: 4px 0px;
            }
        """)
        audio_settings_layout = QGridLayout(self.audio_settings_frame)
        audio_settings_layout.setSpacing(10)
        
        # 音频比特率
        bitrate_label = QLabel("音频比特率:")
        bitrate_label.setStyleSheet("font-weight: 600; color: #495057;")
        audio_settings_layout.addWidget(bitrate_label, 0, 0)
        
        self.audio_bitrate_combo = QComboBox()
        self.audio_bitrate_combo.addItems(["64k", "80k", "96k", "128k", "160k", "192k"])
        self.audio_bitrate_combo.setCurrentText("96k")
        self.audio_bitrate_combo.setStyleSheet("""
            QComboBox {
                min-height: 26px;
                font-size: 13px;
                background-color: #ffffff;
            }
        """)
        self.audio_bitrate_combo.currentTextChanged.connect(self.on_settings_changed)
        audio_settings_layout.addWidget(self.audio_bitrate_combo, 0, 1)
        
        # 音频编码器
        codec_label = QLabel("音频编码:")
        codec_label.setStyleSheet("font-weight: 600; color: #495057;")
        audio_settings_layout.addWidget(codec_label, 1, 0)
        
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.setStyleSheet("""
            QComboBox {
                min-height: 26px;
                font-size: 13px;
                background-color: #ffffff;
            }
        """)
        audio_codecs = compression_presets.AUDIO_CODECS
        for codec_key, codec_data in audio_codecs.items():
            self.audio_codec_combo.addItem(f"{codec_data['name']} - {codec_data['description']}", codec_key)
        self.audio_codec_combo.currentTextChanged.connect(self.on_settings_changed)
        audio_settings_layout.addWidget(self.audio_codec_combo, 1, 1)
        
        # 音频提示
        audio_hint = QLabel("🎧 建议: 语音内容使用64k，音乐内容使用128k或更高")
        audio_hint.setStyleSheet("""
            color: #6c757d;
            font-size: 11px;
            font-style: italic;
            background-color: #e3f2fd;
            padding: 6px 10px;
            border-radius: 4px;
            border-left: 3px solid #2196f3;
            margin: 4px 0px;
        """)
        audio_settings_layout.addWidget(audio_hint, 2, 0, 1, 2)
        
        audio_layout.addWidget(self.audio_settings_frame)
        parent_layout.addWidget(audio_group)
        
    def create_advanced_section(self, parent_layout):
        """创建高级设置区域"""
        advanced_group = QGroupBox("⚙️ 高级设置")
        advanced_group.setStyleSheet("""
            QGroupBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #fff8e1, stop:1 #f5f5f5);
                border: 2px solid #ff9800;
            }
            QGroupBox::title {
                background-color: #fff8e1;
                border: 2px solid #ff9800;
                color: #e65100;
            }
        """)
        advanced_layout = QGridLayout(advanced_group)
        advanced_layout.setSpacing(12)
        
        # 编码器选择
        codec_label = QLabel("视频编码器:")
        codec_label.setStyleSheet("font-weight: 600; color: #495057;")
        advanced_layout.addWidget(codec_label, 0, 0)
        
        self.video_codec_combo = QComboBox()
        self.video_codec_combo.setStyleSheet("""
            QComboBox {
                min-height: 28px;
                font-size: 13px;
                background-color: #ffffff;
                font-weight: 500;
            }
        """)
        video_codecs = compression_presets.VIDEO_CODECS
        for codec_key, codec_data in video_codecs.items():
            display_text = f"{codec_data['name']} - {codec_data['compatibility']}"
            self.video_codec_combo.addItem(display_text, codec_key)
        self.video_codec_combo.currentTextChanged.connect(self.on_settings_changed)
        advanced_layout.addWidget(self.video_codec_combo, 0, 1)
        
        # 编码预设
        preset_label = QLabel("编码速度:")
        preset_label.setStyleSheet("font-weight: 600; color: #495057;")
        advanced_layout.addWidget(preset_label, 1, 0)
        
        self.encode_preset_combo = QComboBox()
        self.encode_preset_combo.setStyleSheet("""
            QComboBox {
                min-height: 28px;
                font-size: 13px;
                background-color: #ffffff;
                font-weight: 500;
            }
        """)
        
        # 编码预设选项与说明
        encode_presets = [
            ("ultrafast", "ultrafast - 最快速度，文件最大"),
            ("superfast", "superfast - 超快速度"),
            ("veryfast", "veryfast - 很快速度"),
            ("faster", "faster - 较快速度"),
            ("fast", "fast - 快速度"),
            ("medium", "medium - 平衡速度与质量 (推荐)"),
            ("slow", "slow - 慢速度，质量较好"),
            ("slower", "slower - 更慢速度"),
            ("veryslow", "veryslow - 最慢速度，质量最佳")
        ]
        
        for preset_key, preset_desc in encode_presets:
            self.encode_preset_combo.addItem(preset_desc, preset_key)
        
        self.encode_preset_combo.setCurrentText("medium - 平衡速度与质量 (推荐)")
        self.encode_preset_combo.currentTextChanged.connect(self.on_settings_changed)
        advanced_layout.addWidget(self.encode_preset_combo, 1, 1)
        
        # 高级设置提示
        advanced_hint = QLabel("⚠️ 高级用户选项：修改这些设置可能影响压缩效果和兼容性")
        advanced_hint.setStyleSheet("""
            color: #6c757d;
            font-size: 11px;
            font-style: italic;
            background-color: #fff3cd;
            padding: 6px 10px;
            border-radius: 4px;
            border-left: 3px solid #ff9800;
            margin: 4px 0px;
        """)
        advanced_layout.addWidget(advanced_hint, 2, 0, 1, 2)
        
        parent_layout.addWidget(advanced_group)
        
    def on_preset_changed(self):
        """处理预设变化"""
        preset_key = self.preset_combo.currentData()
        if preset_key:
            self.load_preset(preset_key)
            
    def load_preset(self, preset_key: str):
        """加载指定预设"""
        self.current_preset = preset_key
        preset_data = compression_presets.get_preset(preset_key)
        
        # 更新预设描述
        display_info = compression_presets.get_preset_display_info(preset_key)
        description_text = f"""
        <b>{display_info['description']}</b><br/>
        <small><b>适用场景:</b> {display_info['use_case']}</small>
        """
        self.preset_description.setText(description_text)
        
        # 更新质量设置
        crf_value = preset_data['video']['crf']
        self.crf_slider.setValue(crf_value)
        
        # 更新音频设置
        audio_bitrate = preset_data['audio']['bitrate']
        self.audio_bitrate_combo.setCurrentText(audio_bitrate)
        
        audio_codec = preset_data['audio']['codec']
        for i in range(self.audio_codec_combo.count()):
            if self.audio_codec_combo.itemData(i) == audio_codec:
                self.audio_codec_combo.setCurrentIndex(i)
                break
        
        # 更新高级设置
        video_codec = preset_data['video']['codec']
        for i in range(self.video_codec_combo.count()):
            if self.video_codec_combo.itemData(i) == video_codec:
                self.video_codec_combo.setCurrentIndex(i)
                break
                
        encode_preset = preset_data['video']['preset']
        for i in range(self.encode_preset_combo.count()):
            if self.encode_preset_combo.itemData(i) == encode_preset:
                self.encode_preset_combo.setCurrentIndex(i)
                break
        
        # 更新当前设置并发出信号
        self.update_current_settings()
        
    def on_audio_settings_changed(self):
        """处理音频设置变化"""
        is_audio_enabled = self.keep_audio_checkbox.isChecked()
        self.audio_settings_frame.setEnabled(is_audio_enabled)
        self.on_settings_changed()
        
    def on_settings_changed(self):
        """处理设置变化"""
        self.update_current_settings()
        
    def update_crf_label(self, value):
        """更新CRF质量标签"""
        quality_levels = {
            (15, 18): ("最高", "#e74c3c", "🌟"),
            (19, 21): ("很高", "#f39c12", "⭐"),  
            (22, 25): ("标准", "#007bff", "✓"),
            (26, 28): ("较低", "#28a745", "📉"),
            (29, 35): ("最低", "#6c757d", "💾")
        }
        
        quality_text = "标准"
        quality_color = "#007bff"
        quality_icon = "✓"
        
        for (min_val, max_val), (text, color, icon) in quality_levels.items():
            if min_val <= value <= max_val:
                quality_text = text
                quality_color = color
                quality_icon = icon
                break
        
        self.crf_label.setText(f"{quality_icon} {value} ({quality_text})")
        self.crf_label.setStyleSheet(f"""
            background-color: {quality_color};
            color: white;
            padding: 6px 12px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            font-size: 13px;
            min-width: 90px;
        """)
        
    def update_current_settings(self):
        """更新当前设置并发出信号"""
        # 获取当前所有设置
        resolution_key = self.resolution_combo.currentData()
        framerate_key = self.framerate_combo.currentData()
        
        resolution_data = compression_presets.RESOLUTION_PRESETS.get(resolution_key, {})
        framerate_data = compression_presets.FRAMERATE_PRESETS.get(framerate_key, {})
        
        self.current_settings = {
            "preset": self.current_preset,
            "crf": self.crf_slider.value(),
            "keep_audio": self.keep_audio_checkbox.isChecked(),
            "audio_bitrate": self.audio_bitrate_combo.currentText(),
            "audio_codec": self.audio_codec_combo.currentData(),
            "video_codec": self.video_codec_combo.currentData(),
            "encode_preset": self.encode_preset_combo.currentData(),
            "resolution": {
                "key": resolution_key,
                "width": resolution_data.get("width"),
                "height": resolution_data.get("height")
            },
            "framerate": {
                "key": framerate_key,
                "fps": framerate_data.get("fps")
            }
        }
        
        # 发出设置变化信号
        self.settings_changed.emit(self.current_settings)
        
    def get_current_settings(self) -> dict:
        """获取当前设置"""
        return self.current_settings.copy()
        
    def reset_to_defaults(self):
        """重置为默认设置"""
        self.load_preset("standard")
        
    def is_valid_settings(self) -> bool:
        """检查当前设置是否有效"""
        return bool(self.current_settings) 