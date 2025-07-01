# VideoCompressor - 视频压缩工具

<div align="center">

![VideoCompressor Logo](resources/icons/default_icon.png)

**现代化视频压缩工具 - 简单易用的界面化视频处理解决方案**

[![Release](https://img.shields.io/github/v/release/lyman86/video-compressor)](https://github.com/lyman86/video-compressor/releases)
[![Build Status](https://img.shields.io/github/actions/workflow/status/lyman86/video-compressor/build.yml)](https://github.com/lyman86/video-compressor/actions)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey.svg)](#下载)

</div>

## 📝 项目简介

VideoCompressor 是一款功能强大且易于使用的视频压缩工具，采用现代化的图形界面设计，支持多种视频格式的高效压缩。无论您是内容创作者、视频编辑师还是普通用户，都能轻松上手使用。

### 🌟 主要特性

- **🎯 智能压缩预设**：提供5种预设方案（高质量、标准、高压缩、网络优化、自定义）
- **🎨 现代化界面**：基于PyQt5构建的美观用户界面，支持拖拽操作
- **⚙️ 灵活配置**：支持自定义视频质量、分辨率、帧率、音频设置等参数
- **📱 跨平台支持**：完美支持Windows和macOS系统
- **🚀 高效处理**：基于FFmpeg引擎，提供专业级视频处理能力
- **📊 实时进度**：可视化压缩进度和状态显示
- **🔧 自动管理**：内置FFmpeg自动下载和管理功能

## 🎯 功能亮点

### 压缩预设方案
| 预设类型 | CRF值 | 适用场景 | 特点 |
|---------|-------|----------|------|
| **🌟 高质量** | 18-20 | 专业视频、存档 | 近无损压缩，文件较大 |
| **⚖️ 标准** | 23-25 | 日常使用、分享 | 质量与大小平衡 |
| **💾 高压缩** | 28-30 | 网络传输、存储 | 大幅减小文件大小 |
| **🌐 网络优化** | 26-28 | 在线播放、流媒体 | 针对网络传输优化 |
| **🔧 自定义** | 15-35 | 专业需求 | 完全自定义参数 |

### 支持格式
- **输入格式**：MP4, AVI, MOV, MKV, WMV, FLV, 3GP 等主流格式
- **输出格式**：MP4（推荐）、AVI 等
- **视频编码**：H.264, H.265/HEVC
- **音频编码**：AAC, MP3

## 📥 下载安装

### 直接下载（推荐）
访问 [Releases 页面](https://github.com/lyman86/video-compressor/releases) 下载最新版本：

- **Windows**: `VideoCompressor-Windows.zip`
- **macOS**: `VideoCompressor-macOS.zip`

### 系统要求
- **Windows**: Windows 10 或更高版本（64位）
- **macOS**: macOS 10.14 或更高版本
- **内存**: 建议4GB以上
- **存储**: 100MB可用空间

## 🚀 快速开始

### 1. 安装步骤
1. 下载对应平台的压缩包
2. 解压到任意目录
3. 双击运行 `VideoCompressor.exe`（Windows）或 `VideoCompressor`（macOS）

### 2. 基本使用
1. **选择视频文件**：拖拽视频文件到程序窗口，或点击选择文件
2. **选择压缩预设**：根据需求选择合适的压缩方案
3. **调整参数**（可选）：自定义质量、分辨率、音频设置等
4. **开始压缩**：点击"开始压缩"按钮
5. **等待完成**：查看实时进度，压缩完成后可直接打开文件位置

### 3. 高级功能
- **质量控制**：使用CRF滑块精确控制视频质量
- **分辨率调整**：支持原始、4K、1080p、720p等预设
- **音频处理**：可选择保留、移除音频或调整音频参数
- **编码优化**：选择编码速度预设平衡处理时间和质量

## 🛠️ 技术栈

### 核心技术
- **界面框架**：PyQt5 - 现代化GUI框架
- **视频处理**：FFmpeg - 专业级多媒体处理引擎
- **编程语言**：Python 3.8+ - 高效开发语言
- **打包工具**：PyInstaller - 跨平台应用打包

### 项目架构
```
video/
├── app/                    # 应用核心模块
│   ├── core/              # 核心功能
│   │   ├── compression_presets.py    # 压缩预设
│   │   ├── compression_thread.py     # 压缩线程
│   │   ├── ffmpeg_manager.py        # FFmpeg管理
│   │   └── video_compressor.py      # 压缩引擎
│   ├── widgets/           # UI组件
│   │   ├── compression_settings_widget.py  # 设置面板
│   │   ├── file_drop_widget.py            # 文件拖拽
│   │   └── ffmpeg_install_dialog.py       # 安装对话框
│   └── main_window.py     # 主窗口
├── resources/             # 资源文件
│   ├── icons/            # 图标资源
│   ├── styles/           # 样式文件
│   └── ffmpeg/          # FFmpeg二进制
├── main.py               # 程序入口
└── requirements.txt      # 依赖列表
```

## 🔧 开发指南

### 本地开发环境
```bash
# 克隆项目
git clone https://github.com/lyman86/video-compressor.git
cd video-compressor

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 构建可执行文件
```bash
# 安装构建工具
pip install pyinstaller

# Windows构建
python build_script.py

# 或直接使用PyInstaller
pyinstaller --onefile --windowed --name=VideoCompressor main.py
```

### 自动化构建
项目配置了GitHub Actions自动化构建，推送版本标签即可触发：
```bash
git tag v1.0.x
git push origin v1.0.x
```

## 📊 性能表现

### 压缩效果示例
| 原始大小 | 预设方案 | 压缩后大小 | 压缩率 | 质量评价 |
|---------|---------|-----------|--------|---------|
| 100MB | 高质量 | 85MB | 15% | 几乎无损 |
| 100MB | 标准 | 65MB | 35% | 优秀 |
| 100MB | 高压缩 | 45MB | 55% | 良好 |
| 100MB | 网络优化 | 50MB | 50% | 适合流媒体 |

### 处理速度
- **CPU使用**：充分利用多核处理器
- **内存占用**：通常低于500MB
- **处理速度**：1080p视频约为实时播放的2-5倍速度（取决于硬件配置）

## 🤝 贡献指南

欢迎为项目做出贡献！您可以：

1. **报告问题**：在 [Issues](https://github.com/lyman86/video-compressor/issues) 中提交bug报告
2. **功能建议**：提出新功能想法和改进建议
3. **代码贡献**：提交Pull Request
4. **文档改进**：帮助完善文档和使用指南

### 开发规范
- 遵循Python PEP8代码规范
- 提交前进行代码测试
- 添加必要的注释和文档
- 保持向后兼容性

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 🙏 致谢

- **FFmpeg**: 强大的多媒体处理框架
- **PyQt5**: 优秀的Python GUI框架
- **社区贡献者**: 感谢所有参与项目的开发者

## 📞 联系方式

- **项目地址**: [https://github.com/lyman86/video-compressor](https://github.com/lyman86/video-compressor)
- **问题反馈**: [Issues](https://github.com/lyman86/video-compressor/issues)
- **功能建议**: [Discussions](https://github.com/lyman86/video-compressor/discussions)

---

<div align="center">

**如果这个项目对您有帮助，请考虑给个 ⭐ Star！**

Made with ❤️ by [Lyman86](https://github.com/lyman86)

</div> 