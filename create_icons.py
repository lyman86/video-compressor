#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用图标创建脚本
从PNG图片生成ICO（Windows）和ICNS（macOS）格式图标
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def install_pillow():
    """安装Pillow库"""
    try:
        from PIL import Image
        print("✅ Pillow已安装")
        return True
    except ImportError:
        print("📦 正在安装Pillow...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'])
            print("✅ Pillow安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ Pillow安装失败")
            return False

def create_ico_icon(png_path: str, ico_path: str):
    """创建Windows ICO图标"""
    try:
        from PIL import Image
        
        # 打开PNG图片
        img = Image.open(png_path).convert('RGBA')
        
        # 生成多种尺寸
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icon_images = []
        
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        # 保存为ICO文件
        icon_images[0].save(ico_path, format='ICO', sizes=[img.size for img in icon_images])
        print(f"✅ 已创建Windows图标: {ico_path}")
        return True
        
    except Exception as e:
        print(f"❌ 创建ICO图标失败: {e}")
        return False

def create_icns_icon_with_sips(png_path: str, icns_path: str):
    """使用macOS sips命令创建ICNS图标"""
    try:
        # 创建iconset目录
        iconset_dir = Path(icns_path).with_suffix('.iconset')
        iconset_dir.mkdir(exist_ok=True)
        
        # 定义所需的图标尺寸
        sizes = [
            (16, 'icon_16x16.png'),
            (32, 'icon_16x16@2x.png'),
            (32, 'icon_32x32.png'),
            (64, 'icon_32x32@2x.png'),
            (128, 'icon_128x128.png'),
            (256, 'icon_128x128@2x.png'),
            (256, 'icon_256x256.png'),
            (512, 'icon_256x256@2x.png'),
            (512, 'icon_512x512.png'),
            (1024, 'icon_512x512@2x.png'),
        ]
        
        # 生成各种尺寸的PNG
        for size, filename in sizes:
            output_path = iconset_dir / filename
            cmd = ['sips', '-z', str(size), str(size), png_path, '--out', str(output_path)]
            subprocess.run(cmd, check=True, capture_output=True)
        
        # 转换为ICNS
        cmd = ['iconutil', '-c', 'icns', str(iconset_dir), '-o', icns_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # 清理临时目录
        import shutil
        shutil.rmtree(iconset_dir)
        
        print(f"✅ 已创建macOS图标: {icns_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 使用sips创建ICNS图标失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 创建ICNS图标失败: {e}")
        return False

def create_icns_icon_with_pillow(png_path: str, icns_path: str):
    """使用Pillow创建ICNS图标（跨平台）"""
    try:
        from PIL import Image
        
        # 打开PNG图片
        img = Image.open(png_path).convert('RGBA')
        
        # 生成多种尺寸
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        icon_images = []
        
        for size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        # 保存为ICNS文件（需要pillow-icns插件）
        try:
            icon_images[0].save(icns_path, format='ICNS', append_images=icon_images[1:])
            print(f"✅ 已创建macOS图标: {icns_path}")
            return True
        except Exception:
            # 如果直接保存失败，尝试安装pillow-icns
            print("📦 正在安装pillow-icns插件...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pillow-icns'])
            icon_images[0].save(icns_path, format='ICNS', append_images=icon_images[1:])
            print(f"✅ 已创建macOS图标: {icns_path}")
            return True
            
    except Exception as e:
        print(f"❌ 使用Pillow创建ICNS图标失败: {e}")
        return False

def create_default_icon():
    """创建默认图标"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建256x256的图像
        size = 256
        img = Image.new('RGBA', (size, size))  # 默认透明背景
        draw = ImageDraw.Draw(img)
        
        # 绘制圆形背景
        margin = 20
        circle_bbox = [margin, margin, size-margin, size-margin]
        draw.ellipse(circle_bbox, fill='#007bff', outline='#0056b3', width=4)
        
        # 绘制播放图标（三角形）
        triangle_size = 60
        center_x, center_y = size // 2, size // 2
        triangle_points = [
            (center_x - triangle_size//2, center_y - triangle_size//2),
            (center_x - triangle_size//2, center_y + triangle_size//2),
            (center_x + triangle_size//2, center_y)
        ]
        draw.polygon(triangle_points, fill='white')
        
        # 保存为PNG
        png_path = 'resources/icons/default_icon.png'
        os.makedirs(os.path.dirname(png_path), exist_ok=True)
        img.save(png_path)
        
        print(f"✅ 已创建默认图标: {png_path}")
        return png_path
        
    except Exception as e:
        print(f"❌ 创建默认图标失败: {e}")
        return None

def main():
    """主函数"""
    print("🎨 应用图标创建工具")
    print("=" * 40)
    
    # 检查并安装Pillow
    if not install_pillow():
        sys.exit(1)
    
    # 获取PNG图片路径
    png_path = input("请输入PNG图片路径（留空使用默认图标）: ").strip()
    
    if not png_path:
        # 创建默认图标
        png_path = create_default_icon()
        if not png_path:
            sys.exit(1)
    else:
        # 检查文件是否存在
        if not os.path.exists(png_path):
            print(f"❌ 文件不存在: {png_path}")
            sys.exit(1)
    
    # 创建图标目录
    icons_dir = Path('resources/icons')
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    # 图标输出路径
    ico_path = str(icons_dir / 'app.ico')
    icns_path = str(icons_dir / 'app.icns')
    
    print(f"\n📂 输入图片: {png_path}")
    print(f"📁 输出目录: {icons_dir}")
    
    # 创建Windows图标
    print("\n🪟 创建Windows图标...")
    if create_ico_icon(png_path, ico_path):
        print(f"   {ico_path}")
    
    # 创建macOS图标
    print("\n🍎 创建macOS图标...")
    
    # 在macOS上优先使用sips
    if platform.system() == 'Darwin':
        if not create_icns_icon_with_sips(png_path, icns_path):
            print("   尝试使用Pillow...")
            create_icns_icon_with_pillow(png_path, icns_path)
    else:
        create_icns_icon_with_pillow(png_path, icns_path)
    
    print(f"\n🎉 图标创建完成！")
    print(f"   Windows: {ico_path}")
    print(f"   macOS: {icns_path}")
    print(f"\n💡 现在可以运行 python build_script.py 进行打包")

if __name__ == '__main__':
    main() 