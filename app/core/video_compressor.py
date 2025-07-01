#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频压缩核心处理器 - 使用FFmpeg进行视频压缩
"""

import os
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from app.core.compression_presets import compression_presets
from app.core.ffmpeg_manager import ffmpeg_manager


class VideoCompressor:
    """视频压缩处理器"""
    
    def __init__(self):
        self.ffmpeg_manager = ffmpeg_manager
        self.current_process = None
        self.is_cancelling = False
        
    def compress_video(self, 
                      input_file: str, 
                      output_file: str, 
                      settings: Dict[str, Any], 
                      progress_callback: Optional[Callable[[int, str], None]] = None,
                      error_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        压缩视频文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径  
            settings: 压缩设置字典
            progress_callback: 进度回调函数 (progress_percent, status_message)
            error_callback: 错误回调函数 (error_message)
            
        Returns:
            bool: 压缩是否成功
        """
        try:
            # 检查FFmpeg可用性
            ffmpeg_info = self.ffmpeg_manager.get_ffmpeg_info()
            if not ffmpeg_info["available"]:
                if error_callback:
                    error_callback("FFmpeg未安装或不可用")
                return False
            
            # 检查输入文件
            if not Path(input_file).exists():
                if error_callback:
                    error_callback(f"输入文件不存在: {input_file}")
                return False
            
            # 创建输出目录
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 构建FFmpeg命令
            cmd = self._build_ffmpeg_command(input_file, output_file, settings)
            
            if progress_callback:
                progress_callback(0, "开始压缩...")
            
            # 获取视频时长用于计算进度
            duration = self._get_video_duration(input_file)
            
            # 执行压缩
            success = self._execute_compression(cmd, duration, progress_callback, error_callback)
            
            if success and not self.is_cancelling:
                if progress_callback:
                    progress_callback(100, "压缩完成")
                return True
            else:
                return False
                
        except Exception as e:
            if error_callback:
                error_callback(f"压缩过程中发生错误: {str(e)}")
            return False
    
    def _build_ffmpeg_command(self, input_file: str, output_file: str, settings: Dict[str, Any]) -> list:
        """构建FFmpeg命令"""
        # 获取预设配置
        preset_name = settings.get("preset", "standard")
        preset_data = compression_presets.get_preset(preset_name)
        
        # 使用用户自定义设置覆盖预设
        if settings.get("crf"):
            preset_data["video"]["crf"] = settings["crf"]
        
        if settings.get("video_codec"):
            preset_data["video"]["codec"] = settings["video_codec"]
            
        if settings.get("encode_preset"):
            preset_data["video"]["preset"] = settings["encode_preset"]
        
        if settings.get("audio_bitrate"):
            preset_data["audio"]["bitrate"] = settings["audio_bitrate"]
            
        if settings.get("audio_codec"):
            preset_data["audio"]["codec"] = settings["audio_codec"]
        
        # 构建分辨率参数
        resolution = settings.get("resolution", {})
        custom_resolution = None
        if resolution.get("width") and resolution.get("height"):
            custom_resolution = (resolution["width"], resolution["height"])
        
        # 构建帧率参数
        framerate = settings.get("framerate", {})
        custom_framerate = framerate.get("fps")
        
        # 保留音频设置
        keep_audio = settings.get("keep_audio", True)
        
        # 使用预设管理器生成FFmpeg参数
        args = compression_presets.get_ffmpeg_args(
            preset_data, 
            input_file, 
            output_file,
            keep_audio=keep_audio,
            custom_resolution=custom_resolution if custom_resolution else None,
            custom_framerate=custom_framerate
        )
        
        # 获取FFmpeg可执行文件路径
        ffmpeg_path = self.ffmpeg_manager.get_ffmpeg_info()["path"]
        
        # 构建完整命令，添加进度和统计信息输出
        cmd = [ffmpeg_path]
        cmd.extend(["-y"])  # 覆盖输出文件
        cmd.extend(["-i", input_file])
        cmd.extend(args[2:-1])  # 排除输入和输出文件部分
        cmd.extend(["-progress", "pipe:2"])  # 进度输出到stderr
        cmd.extend(["-stats"])  # 显示统计信息
        cmd.append(output_file)
        
        return cmd
    
    def _get_video_duration(self, input_file: str) -> float:
        """获取视频时长（秒）"""
        try:
            ffmpeg_path = self.ffmpeg_manager.get_ffmpeg_info()["path"]
            cmd = [
                ffmpeg_path,
                "-i", input_file,
                "-f", "null", "-"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 添加超时
            )
            
            # 从stderr中提取时长信息（FFmpeg信息输出到stderr）
            output_text = result.stderr
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.?\d*)', output_text)
            if duration_match:
                hours = int(duration_match.group(1))
                minutes = int(duration_match.group(2))
                seconds = float(duration_match.group(3))
                total_seconds = hours * 3600 + minutes * 60 + seconds
                print(f"检测到视频时长: {total_seconds:.2f}秒")
                return total_seconds
            
            # 如果没有找到时长，尝试其他方法
            print(f"未能从FFmpeg输出中提取时长，输出: {output_text[:200]}")
            return 0.0
            
        except subprocess.TimeoutExpired:
            print("获取视频时长超时")
            return 0.0
        except Exception as e:
            print(f"获取视频时长失败: {e}")
            return 0.0
    
    def _execute_compression(self, cmd: list, duration: float, 
                           progress_callback: Optional[Callable], 
                           error_callback: Optional[Callable]) -> bool:
        """执行压缩命令"""
        try:
            self.is_cancelling = False
            
            print(f"执行FFmpeg命令: {' '.join(cmd)}")
            
            # 启动FFmpeg进程
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                bufsize=1  # 行缓冲
            )
            
            # 监控进度
            return self._monitor_progress(duration, progress_callback, error_callback)
            
        except Exception as e:
            if error_callback:
                error_callback(f"执行压缩命令失败: {str(e)}")
            return False
    
    def _monitor_progress(self, duration: float, 
                         progress_callback: Optional[Callable], 
                         error_callback: Optional[Callable]) -> bool:
        """监控压缩进度"""
        try:
            error_output = ""
            last_progress_time = time.time()
            timeout_seconds = 300  # 5分钟超时
            
            # 读取进度输出
            while True:
                if self.is_cancelling:
                    self.cancel_compression()
                    return False
                
                # 检查进程是否结束
                if not self.current_process or self.current_process.poll() is not None:
                    break
                
                # 检查超时
                if time.time() - last_progress_time > timeout_seconds:
                    if error_callback:
                        error_callback("压缩超时，可能是文件过大或参数设置问题")
                    self.cancel_compression()
                    return False
                
                try:
                    # 使用select模拟非阻塞读取（仅适用于Unix系统）
                    import select
                    ready, _, _ = select.select([self.current_process.stderr], [], [], 0.1)
                    
                    if ready:
                        line = self.current_process.stderr.readline()
                        if line:
                            line = line.strip()
                            # 解析进度信息
                            if self._parse_progress_line(line, duration, progress_callback):
                                last_progress_time = time.time()
                            # 收集错误输出
                            if "error" in line.lower() or "failed" in line.lower():
                                error_output += line + "\n"
                    
                    # 也读取stdout以防遗漏
                    ready_out, _, _ = select.select([self.current_process.stdout], [], [], 0.1)
                    if ready_out:
                        out_line = self.current_process.stdout.readline()
                        if out_line:
                            print(f"FFmpeg stdout: {out_line.strip()}")
                            
                except ImportError:
                    # Windows系统不支持select，使用阻塞读取但加短超时
                    try:
                        if self.current_process:
                            line = self.current_process.stderr.readline()
                            if line:
                                line = line.strip()
                                if self._parse_progress_line(line, duration, progress_callback):
                                    last_progress_time = time.time()
                                if "error" in line.lower() or "failed" in line.lower():
                                    error_output += line + "\n"
                    except:
                        pass
                    
                    time.sleep(0.1)
                
                except Exception as e:
                    print(f"读取FFmpeg输出时出错: {e}")
                    time.sleep(0.1)
            
            # 检查最终结果
            return_code = self.current_process.returncode if self.current_process else -1
            if return_code == 0:
                return True
            else:
                # 收集剩余的错误输出
                try:
                    if self.current_process:
                        remaining_error = self.current_process.stderr.read()
                        if remaining_error:
                            error_output += remaining_error
                except:
                    pass
                    
                if error_callback:
                    error_msg = f"压缩失败 (返回码: {return_code})"
                    if error_output.strip():
                        error_msg += f"\n错误信息: {error_output.strip()}"
                    error_callback(error_msg)
                return False
                
        except Exception as e:
            if error_callback:
                error_callback(f"监控进度时发生错误: {str(e)}")
            return False
    
    def _parse_progress_line(self, line: str, duration: float, progress_callback: Optional[Callable]) -> bool:
        """解析FFmpeg进度输出，返回是否解析到有效进度"""
        try:
            if not progress_callback:
                return False
            
            # 解析时间进度 (out_time_us=微秒)
            if line.startswith("out_time_us="):
                time_us_str = line.split("=")[1].strip()
                if time_us_str and time_us_str != "N/A":
                    time_us = int(time_us_str)
                    current_time = time_us / 1000000.0  # 转换为秒
                    
                    if duration > 0:
                        # 计算进度百分比
                        progress = min(100, int((current_time / duration) * 100))
                        
                        # 格式化状态消息
                        current_time_str = self._format_time(current_time)
                        total_time_str = self._format_time(duration)
                        status_msg = f"正在压缩... {current_time_str}/{total_time_str} ({progress}%)"
                        
                        progress_callback(progress, status_msg)
                        return True
                    else:
                        # 没有总时长，只显示当前时间
                        current_time_str = self._format_time(current_time)
                        status_msg = f"正在压缩... {current_time_str}"
                        progress_callback(None, status_msg)
                        return True
            
            # 解析帧数进度
            elif line.startswith("frame="):
                frame_match = re.search(r'frame=\s*(\d+)', line)
                if frame_match:
                    frame_num = int(frame_match.group(1))
                    if frame_num > 0:
                        status_msg = f"正在处理第 {frame_num} 帧..."
                        progress_callback(None, status_msg)
                        return True
            
            # 解析速度信息
            elif "speed=" in line:
                speed_match = re.search(r'speed=\s*([\d.]+)x', line)
                if speed_match:
                    speed = float(speed_match.group(1))
                    status_msg = f"处理速度: {speed:.1f}x"
                    progress_callback(None, status_msg)
                    return True
            
            return False
            
        except Exception as e:
            print(f"解析进度行失败: {e}, 行内容: {line}")
            return False
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def cancel_compression(self):
        """取消当前压缩任务"""
        self.is_cancelling = True
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
                time.sleep(1)
                if self.current_process.poll() is None:
                    self.current_process.kill()
            except Exception as e:
                print(f"取消压缩任务失败: {e}")
    
    def is_compression_running(self) -> bool:
        """检查是否有压缩任务正在运行"""
        return (self.current_process is not None and 
                self.current_process.poll() is None and 
                not self.is_cancelling)
    
    def get_estimated_output_size(self, input_file: str, settings: Dict[str, Any]) -> Optional[int]:
        """估算输出文件大小（字节）"""
        try:
            input_size = Path(input_file).stat().st_size
            
            # 根据压缩比例估算
            preset_name = settings.get("preset", "standard")
            preset_data = compression_presets.get_preset(preset_name)
            compression_ratio = preset_data.get("compression_ratio", "50%")
            
            # 解析压缩比例
            ratio_match = re.search(r'(\d+)%', compression_ratio)
            if ratio_match:
                ratio = int(ratio_match.group(1)) / 100.0
                estimated_size = int(input_size * (1 - ratio))
                return max(estimated_size, input_size // 10)  # 最小为原文件的10%
            
            return input_size // 2  # 默认估算为原文件的一半
            
        except Exception as e:
            print(f"估算文件大小失败: {e}")
            return None


# 全局压缩器实例
video_compressor = VideoCompressor() 