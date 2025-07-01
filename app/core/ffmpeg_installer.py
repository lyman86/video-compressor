#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg自动安装器 - 处理FFmpeg的下载和安装
"""

import os
import sys
import platform
import subprocess
import zipfile
import tarfile
from pathlib import Path
from typing import Optional, Tuple
import requests
from urllib.parse import urlparse


class FFmpegInstaller:
    """FFmpeg自动安装器"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.resources_dir = Path(__file__).parent.parent.parent / "resources"
        self.ffmpeg_dir = self.resources_dir / "ffmpeg"
        self.ffmpeg_dir.mkdir(parents=True, exist_ok=True)
        
        # FFmpeg下载链接配置
        self.download_urls = self._get_download_urls()
    
    def _get_download_urls(self) -> dict:
        """获取不同平台的FFmpeg下载链接"""
        urls = {}
        
        if self.system == "darwin":  # macOS
            if "arm" in self.architecture or "aarch64" in self.architecture:
                # Apple Silicon (M1/M2)
                urls["url"] = "https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip"
                urls["type"] = "zip"
            else:
                # Intel Mac
                urls["url"] = "https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip"
                urls["type"] = "zip"
        
        elif self.system == "windows":
            # Windows
            urls["url"] = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            urls["type"] = "zip"
        
        elif self.system == "linux":
            # Linux
            urls["url"] = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
            urls["type"] = "tar.xz"
        
        return urls
    
    def is_ffmpeg_installed(self) -> Tuple[bool, Optional[str]]:
        """检查FFmpeg是否已安装"""
        # 首先检查内嵌的FFmpeg
        embedded_ffmpeg = self.get_embedded_ffmpeg_path()
        if embedded_ffmpeg and embedded_ffmpeg.exists():
            return True, str(embedded_ffmpeg)
        
        # 检查系统路径中的FFmpeg
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # 尝试获取FFmpeg路径
                which_result = subprocess.run(
                    ["which", "ffmpeg"] if self.system != "windows" else ["where", "ffmpeg"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                ffmpeg_path = which_result.stdout.strip() if which_result.returncode == 0 else "system"
                return True, ffmpeg_path
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return False, None
    
    def get_embedded_ffmpeg_path(self) -> Optional[Path]:
        """获取内嵌FFmpeg的路径"""
        if self.system == "windows":
            ffmpeg_exe = self.ffmpeg_dir / "bin" / "ffmpeg.exe"
        else:
            ffmpeg_exe = self.ffmpeg_dir / "ffmpeg"
        
        return ffmpeg_exe if ffmpeg_exe.exists() else None
    
    def install_ffmpeg(self, progress_callback=None) -> Tuple[bool, str]:
        """
        安装FFmpeg
        
        Args:
            progress_callback: 进度回调函数 callback(percentage, message)
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            if not self.download_urls:
                return False, f"不支持的系统平台: {self.system}"
            
            download_url = self.download_urls["url"]
            file_type = self.download_urls["type"]
            
            if progress_callback:
                progress_callback(10, "开始下载FFmpeg...")
            
            # 下载FFmpeg
            download_path = self._download_ffmpeg(download_url, progress_callback)
            if not download_path:
                return False, "FFmpeg下载失败"
            
            if progress_callback:
                progress_callback(70, "正在解压安装...")
            
            # 解压并安装
            success = self._extract_and_install(download_path, file_type)
            
            # 清理下载文件
            try:
                download_path.unlink()
            except:
                pass
            
            if success:
                if progress_callback:
                    progress_callback(100, "安装完成")
                return True, "FFmpeg安装成功"
            else:
                return False, "FFmpeg解压或安装失败"
        
        except Exception as e:
            return False, f"安装过程中出现错误: {str(e)}"
    
    def _download_ffmpeg(self, url: str, progress_callback=None) -> Optional[Path]:
        """下载FFmpeg文件"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # 确定文件名
            parsed_url = urlparse(url)
            filename = Path(parsed_url.path).name
            if not filename or filename == "/":
                filename = f"ffmpeg_download.{self.download_urls['type']}"
            
            download_path = self.ffmpeg_dir / filename
            
            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            percentage = int((downloaded_size / total_size) * 60) + 10  # 10-70%
                            progress_callback(percentage, f"下载中... {downloaded_size // 1024 // 1024}MB")
            
            return download_path
        
        except Exception as e:
            print(f"下载失败: {e}")
            return None
    
    def _extract_and_install(self, archive_path: Path, file_type: str) -> bool:
        """解压并安装FFmpeg"""
        try:
            if file_type == "zip":
                return self._extract_zip(archive_path)
            elif file_type == "tar.xz":
                return self._extract_tar(archive_path)
            else:
                print(f"不支持的文件类型: {file_type}")
                return False
        
        except Exception as e:
            print(f"解压失败: {e}")
            return False
    
    def _extract_zip(self, archive_path: Path) -> bool:
        """解压ZIP文件"""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                # 找到ffmpeg可执行文件
                ffmpeg_files = [name for name in zip_ref.namelist() if 'ffmpeg' in name.lower() and not name.endswith('/')]
                
                if self.system == "darwin":
                    # macOS: 直接提取ffmpeg二进制文件
                    for file_name in ffmpeg_files:
                        if file_name.endswith('ffmpeg') or file_name.endswith('ffmpeg.exe'):
                            zip_ref.extract(file_name, self.ffmpeg_dir)
                            extracted_path = self.ffmpeg_dir / file_name
                            final_path = self.ffmpeg_dir / "ffmpeg"
                            
                            if extracted_path != final_path:
                                extracted_path.rename(final_path)
                            
                            # 设置执行权限
                            final_path.chmod(0o755)
                            return True
                
                elif self.system == "windows":
                    # Windows: 提取整个bin目录
                    zip_ref.extractall(self.ffmpeg_dir)
                    
                    # 查找提取的文件夹并移动内容
                    for item in self.ffmpeg_dir.iterdir():
                        if item.is_dir():
                            bin_dir = item / "bin"
                            if bin_dir.exists():
                                target_bin = self.ffmpeg_dir / "bin"
                                if target_bin.exists():
                                    import shutil
                                    shutil.rmtree(target_bin)
                                bin_dir.rename(target_bin)
                                
                                # 清理临时目录
                                import shutil
                                shutil.rmtree(item)
                                return True
                
                return False
        
        except Exception as e:
            print(f"ZIP解压失败: {e}")
            return False
    
    def _extract_tar(self, archive_path: Path) -> bool:
        """解压TAR文件"""
        try:
            with tarfile.open(archive_path, 'r:xz') as tar_ref:
                # 找到ffmpeg可执行文件
                ffmpeg_files = [member for member in tar_ref.getmembers() if 'ffmpeg' in member.name and member.isfile()]
                
                for member in ffmpeg_files:
                    if member.name.endswith('ffmpeg'):
                        # 提取到临时位置
                        tar_ref.extract(member, self.ffmpeg_dir)
                        extracted_path = self.ffmpeg_dir / member.name
                        final_path = self.ffmpeg_dir / "ffmpeg"
                        
                        # 移动到最终位置
                        extracted_path.rename(final_path)
                        
                        # 设置执行权限
                        final_path.chmod(0o755)
                        
                        # 清理临时目录结构
                        temp_dir = self.ffmpeg_dir / Path(member.name).parts[0]
                        if temp_dir.exists() and temp_dir.is_dir():
                            import shutil
                            shutil.rmtree(temp_dir)
                        
                        return True
                
                return False
        
        except Exception as e:
            print(f"TAR解压失败: {e}")
            return False
    
    def get_ffmpeg_info(self) -> dict:
        """获取FFmpeg信息"""
        info = {
            "installed": False,
            "path": None,
            "version": None,
            "system": self.system,
            "architecture": self.architecture
        }
        
        installed, path = self.is_ffmpeg_installed()
        info["installed"] = installed
        info["path"] = path
        
        if installed and path:
            try:
                # 获取版本信息
                ffmpeg_cmd = path if path != "system" else "ffmpeg"
                result = subprocess.run(
                    [ffmpeg_cmd, "-version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    # 解析版本信息
                    version_line = result.stdout.split('\n')[0]
                    info["version"] = version_line
            
            except Exception as e:
                info["version"] = f"获取版本失败: {e}"
        
        return info 