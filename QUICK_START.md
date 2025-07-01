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