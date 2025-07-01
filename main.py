#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频压缩器主程序入口
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale
from PyQt5.QtGui import QIcon

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.main_window import MainWindow


def main():
    """主函数"""
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("视频压缩器")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("VideoCompressor")
    
    # 设置应用程序图标（如果存在）
    icon_path = Path("resources/icons/app_icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 启动事件循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 