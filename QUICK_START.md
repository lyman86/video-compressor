# VideoCompressor 快速开始指南

## 🚀 5分钟快速上手

### 步骤1：下载安装
1. 访问 [Releases页面](https://github.com/lyman86/video-compressor/releases)
2. 下载对应系统的压缩包：
   - Windows: `VideoCompressor-Windows.zip`  
   - macOS: `VideoCompressor-macOS.zip`
3. 解压到任意文件夹
4. 双击运行程序文件

### 步骤2：压缩视频
1. **添加视频**：拖拽视频文件到程序窗口中央
2. **选择预设**：根据需求选择压缩方案
   - 🌟 **高质量**：适合存档保存
   - ⚖️ **标准**：日常使用推荐
   - 💾 **高压缩**：大幅减小文件
   - 🌐 **网络优化**：在线分享
3. **开始压缩**：点击"开始压缩"按钮
4. **等待完成**：查看进度条，完成后自动打开文件位置

## 🎯 常用设置

### 质量调节
- **CRF值**：数值越小质量越高，文件越大
  - 15-20：高质量（适合专业用途）
  - 21-25：标准质量（推荐）
  - 26-30：高压缩（适合网络传输）

### 分辨率选择
- **保持原始**：不改变分辨率
- **1080p**：适合大多数场景
- **720p**：适合移动设备播放

### 音频处理
- **保留音频**：保持原始音频
- **移除音频**：生成无声视频
- **自定义**：调整音频质量和编码

## ❓ 常见问题

**Q: 程序打不开怎么办？**
A: 确保系统版本符合要求，Windows 10+或macOS 10.14+

**Q: 压缩后视频变模糊？**  
A: 降低CRF值或选择"高质量"预设

**Q: 压缩速度很慢？**
A: 这是正常现象，高质量压缩需要时间，可选择更快的编码预设

**Q: 支持哪些视频格式？**
A: 支持MP4、AVI、MOV、MKV等主流格式

## 🔧 高级技巧

1. **批量处理**：可以连续添加多个视频文件
2. **质量预览**：使用CRF滑块实时查看质量提示
3. **自定义输出**：在设置中指定输出文件夹
4. **暂停恢复**：可以暂停正在进行的压缩任务

需要更详细的说明？查看完整的 [README文档](README.md)。

# 🚀 快速打包指南

## 最简单的打包方法

### 第1步：准备环境
```bash
# 确保安装了所有依赖
pip install -r requirements.txt
```

### 第2步：创建图标（可选）
```bash
# 自动生成默认图标
python create_icons.py

# 或者使用自己的PNG图片
# python create_icons.py
# 然后输入你的PNG文件路径
```

### 第3步：一键打包
```bash
# 运行自动打包脚本
python build_script.py
```

就这么简单！🎉

## 输出结果

⚠️ **重要**：PyInstaller只能为当前运行的平台打包！

### 在macOS上打包
- 输出：`dist/VideoCompressor.app` (仅macOS版本)
- 安装：拖拽到 Applications 文件夹
- 运行：双击应用或从 Launchpad 启动

### 在Windows上打包  
- 输出：`dist/VideoCompressor/VideoCompressor.exe` (仅Windows版本)
- 运行：双击 exe 文件
- 分发：压缩整个 VideoCompressor 文件夹

### 要同时获得两个平台的版本
1. **手动方式**：在不同系统上分别运行打包脚本
2. **自动化方式**：使用GitHub Actions（见下文）

## 常用命令

```bash
# 手动安装 PyInstaller
pip install pyinstaller

# 单文件打包（体积更小，但启动较慢）
pyinstaller --onefile --windowed main.py

# 查看详细错误信息
python build_script.py --verbose

# 清理构建文件
rm -rf build dist *.spec
```

## 疑难解答

### 问题：PyQt5 导入错误
```bash
pip install PyQt5 PyQt5-tools
```

### 问题：FFmpeg 找不到
- 确保 `resources/ffmpeg/` 目录存在
- 检查 FFmpeg 文件权限：`chmod +x resources/ffmpeg/ffmpeg`

### 问题：图标不显示
- 运行 `python create_icons.py` 创建图标
- 或手动放置 app.ico 和 app.icns 到 `resources/icons/`

### 问题：打包文件太大
```bash
# 排除不需要的模块
pyinstaller --exclude-module=tkinter --exclude-module=numpy main.py
```

## 分发建议

### macOS
- 直接分发：压缩 `.app` 文件为 ZIP
- 专业分发：创建 DMG 安装包

### Windows
- 简单分发：压缩 `VideoCompressor` 文件夹
- 专业分发：使用 NSIS 创建安装程序

## 🤖 自动化多平台构建（推荐）

### GitHub Actions方式
1. 将代码推送到GitHub仓库
2. 添加版本标签触发构建：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. 或在GitHub网页上手动触发Actions
4. 等待构建完成，下载两个平台的ZIP包

### 输出文件
- `VideoCompressor-Windows.zip` - Windows版本
- `VideoCompressor-macOS.zip` - macOS版本

---

**💡 提示**：首次打包可能需要下载依赖，请保持网络连接 