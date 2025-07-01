# 视频压缩器打包指南

## 📦 快速开始

### 1. 自动打包（推荐）

```bash
# 运行打包脚本
python build_script.py
```

### 2. 手动打包

```bash
# 安装PyInstaller
pip install pyinstaller

# Mac打包
pyinstaller --name="VideoCompressor" --windowed --icon="resources/icons/app.icns" main.py

# Windows打包
pyinstaller --name="VideoCompressor" --windowed --icon="resources/icons/app.ico" main.py
```

## 🎯 平台特定要求

### macOS 打包

**系统要求**：
- macOS 10.12+ 
- Python 3.8+
- Xcode Command Line Tools

**步骤**：
1. 安装依赖：`pip install -r requirements.txt`
2. 创建图标：将PNG转换为ICNS格式
3. 运行打包：`python build_script.py`
4. 输出：`dist/VideoCompressor.app`

**图标制作**：
```bash
# 使用sips命令转换PNG到ICNS
mkdir app.iconset
sips -z 16 16     icon.png --out app.iconset/icon_16x16.png
sips -z 32 32     icon.png --out app.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out app.iconset/icon_32x32.png
sips -z 64 64     icon.png --out app.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out app.iconset/icon_128x128.png
sips -z 256 256   icon.png --out app.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out app.iconset/icon_256x256.png
sips -z 512 512   icon.png --out app.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out app.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out app.iconset/icon_512x512@2x.png
iconutil -c icns app.iconset
```

### Windows 打包

**系统要求**：
- Windows 10+
- Python 3.8+
- Visual Studio Build Tools（可选）

**步骤**：
1. 安装依赖：`pip install -r requirements.txt`
2. 创建图标：将PNG转换为ICO格式
3. 运行打包：`python build_script.py`
4. 输出：`dist/VideoCompressor/VideoCompressor.exe`

**图标制作**：
- 使用在线工具：https://convertico.com/
- 或使用PIL：
```python
from PIL import Image
img = Image.open('icon.png')
img.save('app.ico', format='ICO', sizes=[(256, 256)])
```

## 🛠️ 高级配置

### 单文件打包

```bash
# 创建单个可执行文件（启动较慢但分发方便）
pyinstaller --onefile --windowed --name="VideoCompressor" main.py
```

### 减小文件大小

```bash
# 排除不必要的模块
pyinstaller --exclude-module=tkinter --exclude-module=matplotlib main.py

# 使用UPX压缩（需要先安装UPX）
pyinstaller --upx-dir=/path/to/upx main.py
```

### 包含FFmpeg

```bash
# 在spec文件中添加FFmpeg二进制文件
datas = [
    ('resources/ffmpeg/ffmpeg', 'resources/ffmpeg/'),  # Unix
    ('resources/ffmpeg/ffmpeg.exe', 'resources/ffmpeg/'),  # Windows
]
```

## 🔧 常见问题

### 1. PyQt5导入错误

**解决方案**：
```bash
pip install PyQt5 PyQt5-tools
```

### 2. FFmpeg路径问题

**症状**：打包后找不到FFmpeg
**解决方案**：
- 确保FFmpeg文件在resources目录
- 检查相对路径配置
- 使用绝对路径或动态路径检测

### 3. 图标不显示

**解决方案**：
- 确保图标格式正确（ICO/ICNS）
- 检查图标文件路径
- 验证图标文件完整性

### 4. 模块导入失败

**解决方案**：
```python
# 在spec文件中添加隐藏导入
hiddenimports = [
    'PyQt5.sip',
    'app.core.video_compressor',
    # ... 其他模块
]
```

### 5. macOS权限问题

**解决方案**：
```bash
# 给应用执行权限
chmod +x dist/VideoCompressor.app/Contents/MacOS/VideoCompressor

# 允许未签名应用（开发测试）
sudo spctl --master-disable
```

### 6. Windows杀毒软件误报

**解决方案**：
- 使用代码签名证书
- 向杀毒软件厂商报告误报
- 从源码编译避免预编译检测

## 📁 文件结构

```
video/
├── main.py                 # 入口文件
├── build_script.py         # 打包脚本
├── requirements.txt        # 依赖列表
├── config.json            # 配置文件
├── app/                   # 应用代码
│   ├── core/              # 核心功能
│   └── widgets/           # UI组件
├── resources/             # 资源文件
│   ├── ffmpeg/           # FFmpeg二进制
│   ├── icons/            # 应用图标
│   └── styles/           # QSS样式
├── build/                # 构建临时文件
└── dist/                 # 打包输出
    ├── VideoCompressor.app    # macOS应用
    └── VideoCompressor/       # Windows应用目录
```

## 🚀 分发建议

### macOS
1. **DMG安装包**：使用create-dmg工具
2. **App Store**：需要开发者账号和代码签名
3. **直接分发**：压缩.app文件为ZIP

### Windows  
1. **安装包**：使用NSIS或Inno Setup
2. **便携版**：直接压缩exe目录
3. **Microsoft Store**：需要开发者账号

### 跨平台
1. **GitHub Releases**：上传各平台版本
2. **官网下载**：提供不同平台链接
3. **自动更新**：集成更新检查功能

## 📝 打包检查清单

- [ ] 安装所有依赖
- [ ] 创建应用图标
- [ ] 测试所有功能
- [ ] 检查资源文件路径
- [ ] 验证FFmpeg可用性
- [ ] 测试文件拖拽功能
- [ ] 检查压缩功能
- [ ] 验证错误处理
- [ ] 测试不同平台
- [ ] 准备分发材料 