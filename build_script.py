#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频压缩器打包脚本
支持Mac和Windows平台
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def get_platform():
    """获取当前平台"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    else:
        return 'unknown'

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
        return True
    except ImportError:
        print("📦 正在安装PyInstaller...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print("✅ PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ PyInstaller安装失败")
            return False

def create_spec_file():
    """创建PyInstaller spec文件"""
    current_platform = get_platform()
    
    # 基础spec内容
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 获取项目根目录
project_dir = Path(SPECPATH)

# 数据文件和资源
datas = [
    (str(project_dir / 'resources'), 'resources'),
    (str(project_dir / 'config.json'), '.'),
]

# 隐藏导入
hiddenimports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'app.core.video_compressor',
    'app.core.compression_thread',
    'app.core.compression_presets',
    'app.core.ffmpeg_manager',
    'app.core.ffmpeg_installer',
    'app.widgets.compression_settings_widget',
    'app.widgets.file_drop_widget',
    'app.widgets.ffmpeg_install_dialog',
]

# 排除的模块
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    'opencv',
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VideoCompressor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,'''
    
    # 添加平台特定图标
    if current_platform == 'windows':
        spec_content += '''
    icon=str(project_dir / 'resources' / 'icons' / 'app.ico'),'''
    elif current_platform == 'macos':
        spec_content += '''
    icon=str(project_dir / 'resources' / 'icons' / 'app.icns'),'''
    
    spec_content += '''
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoCompressor',
)'''
    
    # 添加macOS应用包配置
    if current_platform == 'macos':
        spec_content += '''

app = BUNDLE(
    coll,
    name='VideoCompressor.app',
    icon=str(project_dir / 'resources' / 'icons' / 'app.icns'),
    bundle_identifier='com.videocompressor.app',
    info_plist={
        'CFBundleName': 'Video Compressor',
        'CFBundleDisplayName': '视频压缩器',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.12.0',
    },
)'''
    
    with open('VideoCompressor.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 已创建VideoCompressor.spec文件")

def create_icons():
    """创建应用图标"""
    icons_dir = Path('resources/icons')
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    print("💡 提示：请将以下图标文件放入resources/icons/目录：")
    print("   • app.ico (Windows图标，256x256)")
    print("   • app.icns (macOS图标，1024x1024)")
    print("   • 可以使用在线工具转换PNG到ICO/ICNS格式")

def build_app():
    """执行打包"""
    current_platform = get_platform()
    print(f"🚀 开始为{current_platform}平台打包...")
    
    try:
        # 清理之前的构建
        import shutil
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        
        # 执行PyInstaller
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'VideoCompressor.spec']
        subprocess.check_call(cmd)
        
        print("✅ 打包完成！")
        print(f"📁 输出目录: dist/")
        
        if current_platform == 'macos':
            print("🍎 macOS应用: dist/VideoCompressor.app")
            print("💡 可以拖拽到Applications文件夹安装")
        elif current_platform == 'windows':
            print("🪟 Windows应用: dist/VideoCompressor/VideoCompressor.exe")
            print("💡 可以创建快捷方式或制作安装包")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        return False
    
    return True

def create_installer():
    """创建安装包（可选）"""
    current_platform = get_platform()
    
    if current_platform == 'windows':
        print("\n📦 Windows安装包制作建议：")
        print("   • 使用NSIS或Inno Setup")
        print("   • 或使用pyinstaller --onefile创建单文件")
        
    elif current_platform == 'macos':
        print("\n📦 macOS分发建议：")
        print("   • 使用create-dmg创建DMG安装包")
        print("   • 或直接分发.app文件")

def print_cross_platform_instructions():
    """打印跨平台打包说明"""
    current_platform = get_platform()
    
    print("\n🌍 跨平台打包说明：")
    print("=" * 40)
    
    if current_platform == 'macos':
        print("✅ 已完成macOS版本打包")
        print("🪟 要创建Windows版本，你需要：")
        print("   1. 在Windows电脑上安装Python和依赖")
        print("   2. 复制项目代码到Windows系统")
        print("   3. 运行 python build_script.py")
        print("   4. 或使用虚拟机/云服务器")
        
    elif current_platform == 'windows':
        print("✅ 已完成Windows版本打包")
        print("🍎 要创建macOS版本，你需要：")
        print("   1. 在macOS电脑上安装Python和依赖")
        print("   2. 复制项目代码到macOS系统")
        print("   3. 运行 python build_script.py")
        print("   4. 或使用macOS虚拟机")
    
    print("\n🚀 其他选择：")
    print("   • GitHub Actions：自动化多平台构建")
    print("   • Docker：容器化跨平台打包")
    print("   • 云服务：AWS/Azure虚拟机")

def main():
    """主函数"""
    print("🎬 视频压缩器打包工具")
    print("=" * 50)
    
    current_platform = get_platform()
    print(f"📱 当前平台: {current_platform}")
    
    # 平台限制说明
    if current_platform == 'macos':
        print("⚠️  注意：在macOS上只能打包macOS版本")
        print("📦 输出：VideoCompressor.app (macOS应用)")
        print("🪟 如需Windows版本，请在Windows系统上运行此脚本")
    elif current_platform == 'windows':
        print("⚠️  注意：在Windows上只能打包Windows版本")
        print("📦 输出：VideoCompressor.exe (Windows应用)")
        print("🍎 如需macOS版本，请在macOS系统上运行此脚本")
    
    # 检查依赖
    if not install_pyinstaller():
        sys.exit(1)
    
    # 创建图标目录提示
    create_icons()
    
    # 创建spec文件
    create_spec_file()
    
    # 询问是否继续
    response = input(f"\n是否开始打包{current_platform}版本？(y/N): ").strip().lower()
    if response not in ['y', 'yes', '是']:
        print("取消打包")
        sys.exit(0)
    
    # 执行打包
    if build_app():
        create_installer()
        print("\n🎉 打包完成！")
        print_cross_platform_instructions()
    else:
        print("\n💥 打包失败！")
        sys.exit(1)

if __name__ == '__main__':
    main() 