#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg管理器 - 负责FFmpeg的检测、下载和管理
"""

import os
import sys
import subprocess
import platform
import shutil
import urllib.request
import zipfile
import tarfile
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import json
from .ffmpeg_installer import FFmpegInstaller


class FFmpegManager:
    """FFmpeg管理器类"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.project_root = Path(__file__).parent.parent.parent
        self.ffmpeg_dir = self.project_root / "resources" / "ffmpeg"
        self.ffmpeg_dir.mkdir(parents=True, exist_ok=True)
        
        # FFmpeg下载链接配置
        self.download_urls = {
            "windows": {
                "x64": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
                "x86": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win32-gpl.zip"
            },
            "darwin": {
                "x86_64": "https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip",
                "arm64": "https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip"
            },
            "linux": {
                "x86_64": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",
                "i686": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz"
            }
        }
    
    def get_ffmpeg_path(self) -> Optional[str]:
        """获取FFmpeg可执行文件路径"""
        # 首先检查系统PATH中的FFmpeg
        system_ffmpeg = self.check_system_ffmpeg()
        if system_ffmpeg:
            return system_ffmpeg
        
        # 检查嵌入式FFmpeg
        embedded_ffmpeg = self.check_embedded_ffmpeg()
        if embedded_ffmpeg:
            return embedded_ffmpeg
        
        return None
    
    def check_system_ffmpeg(self) -> Optional[str]:
        """检查系统是否已安装FFmpeg"""
        try:
            ffmpeg_path = shutil.which("ffmpeg")
            if ffmpeg_path:
                # 验证FFmpeg版本
                result = subprocess.run(
                    [ffmpeg_path, "-version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return ffmpeg_path
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return None
    
    def check_embedded_ffmpeg(self) -> Optional[str]:
        """检查嵌入式FFmpeg"""
        if self.system == "windows":
            ffmpeg_exe = self.ffmpeg_dir / "ffmpeg.exe"
        else:
            ffmpeg_exe = self.ffmpeg_dir / "ffmpeg"
        
        if ffmpeg_exe.exists() and os.access(ffmpeg_exe, os.X_OK):
            try:
                result = subprocess.run(
                    [str(ffmpeg_exe), "-version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return str(ffmpeg_exe)
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass
        
        return None
    
    def download_ffmpeg(self, progress_callback=None) -> bool:
        """下载FFmpeg二进制文件"""
        try:
            download_url = self.get_download_url()
            if not download_url:
                return False
            
            # 创建临时下载目录
            temp_dir = self.ffmpeg_dir / "temp"
            temp_dir.mkdir(exist_ok=True)
            
            # 下载文件
            filename = download_url.split("/")[-1]
            temp_file = temp_dir / filename
            
            self._download_file(download_url, temp_file, progress_callback)
            
            # 解压文件
            if self._extract_ffmpeg(temp_file):
                # 清理临时文件
                shutil.rmtree(temp_dir, ignore_errors=True)
                return True
            
        except Exception as e:
            print(f"下载FFmpeg失败: {e}")
        
        return False
    
    def get_download_url(self) -> Optional[str]:
        """获取适合当前平台的下载链接"""
        if self.system not in self.download_urls:
            return None
        
        platform_urls = self.download_urls[self.system]
        
        # 匹配架构
        if self.arch in platform_urls:
            return platform_urls[self.arch]
        
        # 架构别名匹配
        arch_aliases = {
            "amd64": "x86_64",
            "x64": "x86_64",
            "aarch64": "arm64"
        }
        
        for alias, canonical in arch_aliases.items():
            if self.arch == alias and canonical in platform_urls:
                return platform_urls[canonical]
        
        # 默认选择第一个可用的
        return list(platform_urls.values())[0] if platform_urls else None
    
    def _download_file(self, url: str, filepath: Path, progress_callback=None):
        """下载文件并显示进度"""
        def report_progress(block_num, block_size, total_size):
            if progress_callback and total_size > 0:
                progress = min(100, (block_num * block_size / total_size) * 100)
                progress_callback(int(progress))
        
        urllib.request.urlretrieve(url, filepath, reporthook=report_progress)
    
    def _extract_ffmpeg(self, archive_path: Path) -> bool:
        """解压FFmpeg文件"""
        try:
            if archive_path.suffix.lower() == ".zip":
                return self._extract_zip(archive_path)
            elif archive_path.suffix.lower() in [".tar", ".xz"]:
                return self._extract_tar(archive_path)
            
        except Exception as e:
            print(f"解压失败: {e}")
        
        return False
    
    def _extract_zip(self, zip_path: Path) -> bool:
        """解压ZIP文件"""
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 查找ffmpeg可执行文件
            ffmpeg_files = [name for name in zip_ref.namelist() 
                           if name.endswith(('ffmpeg.exe', 'ffmpeg')) and not name.endswith('/')]
            
            if not ffmpeg_files:
                return False
            
            # 解压ffmpeg文件
            ffmpeg_file = ffmpeg_files[0]
            zip_ref.extract(ffmpeg_file, self.ffmpeg_dir)
            
            # 移动到正确位置
            extracted_path = self.ffmpeg_dir / ffmpeg_file
            target_name = "ffmpeg.exe" if self.system == "windows" else "ffmpeg"
            target_path = self.ffmpeg_dir / target_name
            
            shutil.move(extracted_path, target_path)
            
            # 设置执行权限（非Windows系统）
            if self.system != "windows":
                os.chmod(target_path, 0o755)
            
            return True
    
    def _extract_tar(self, tar_path: Path) -> bool:
        """解压TAR文件"""
        with tarfile.open(tar_path, 'r:*') as tar_ref:
            # 查找ffmpeg可执行文件
            ffmpeg_files = [member for member in tar_ref.getmembers() 
                           if member.name.endswith('ffmpeg') and member.isfile()]
            
            if not ffmpeg_files:
                return False
            
            # 解压ffmpeg文件
            ffmpeg_member = ffmpeg_files[0]
            tar_ref.extract(ffmpeg_member, self.ffmpeg_dir)
            
            # 移动到正确位置
            extracted_path = self.ffmpeg_dir / ffmpeg_member.name
            target_path = self.ffmpeg_dir / "ffmpeg"
            
            shutil.move(extracted_path, target_path)
            
            # 设置执行权限
            os.chmod(target_path, 0o755)
            
            return True
    
    def get_ffmpeg_info(self) -> Dict[str, Any]:
        """获取FFmpeg信息"""
        ffmpeg_path = self.get_ffmpeg_path()
        if not ffmpeg_path:
            return {"available": False}
        
        try:
            result = subprocess.run(
                [ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                return {
                    "available": True,
                    "path": ffmpeg_path,
                    "version": version_line,
                    "is_system": ffmpeg_path != str(self.ffmpeg_dir / ("ffmpeg.exe" if self.system == "windows" else "ffmpeg"))
                }
        
        except Exception as e:
            print(f"获取FFmpeg信息失败: {e}")
        
        return {"available": False}
    
    def ensure_ffmpeg_available(self, progress_callback=None) -> bool:
        """确保FFmpeg可用，如果不可用则尝试下载"""
        if self.get_ffmpeg_path():
            return True
        
        print("FFmpeg不可用，正在下载...")
        return self.download_ffmpeg(progress_callback)


# 全局FFmpeg管理器实例
ffmpeg_manager = FFmpegManager() 