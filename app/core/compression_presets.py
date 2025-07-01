#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压缩预设配置 - 定义不同质量等级的压缩参数
"""

from typing import Dict, Any, List


class CompressionPresets:
    """压缩预设管理类"""
    
    # 预设压缩配置
    PRESETS = {
        "high_quality": {
            "name": "高质量",
            "description": "适合存档保存，轻微压缩，保持最佳画质",
            "icon": "🎥",
            "compression_ratio": "30%",
            "use_case": "存档、专业用途、高质量需求",
            "video": {
                "codec": "libx264",
                "crf": 18,
                "preset": "medium",
                "profile": "high",
                "level": "4.1",
                "pixel_format": "yuv420p",
                "tune": None
            },
            "audio": {
                "codec": "aac",
                "bitrate": "128k",
                "sample_rate": 44100,
                "channels": 2
            },
            "filters": [],
            "output_format": "mp4"
        },
        
        "standard": {
            "name": "标准质量",
            "description": "平衡文件大小和画质，适合日常使用",
            "icon": "⚖️",
            "compression_ratio": "50%",
            "use_case": "日常分享、网络传输、一般用途",
            "video": {
                "codec": "libx264",
                "crf": 23,
                "preset": "medium",
                "profile": "high",
                "level": "4.1",
                "pixel_format": "yuv420p",
                "tune": None
            },
            "audio": {
                "codec": "aac",
                "bitrate": "96k",
                "sample_rate": 44100,
                "channels": 2
            },
            "filters": [],
            "output_format": "mp4"
        },
        
        "high_compression": {
            "name": "高压缩",
            "description": "最小文件大小，适合存储空间有限的场景",
            "icon": "📱",
            "compression_ratio": "70%",
            "use_case": "移动设备、网络传输、存储节约",
            "video": {
                "codec": "libx264",
                "crf": 28,
                "preset": "slow",
                "profile": "high",
                "level": "4.1",
                "pixel_format": "yuv420p",
                "tune": None
            },
            "audio": {
                "codec": "aac",
                "bitrate": "64k",
                "sample_rate": 44100,
                "channels": 2
            },
            "filters": [],
            "output_format": "mp4"
        },
        
        "web_optimized": {
            "name": "网络优化",
            "description": "针对网络播放优化，快速加载",
            "icon": "🌐",
            "compression_ratio": "60%",
            "use_case": "网站视频、在线播放、流媒体",
            "video": {
                "codec": "libx264",
                "crf": 25,
                "preset": "fast",
                "profile": "baseline",
                "level": "3.1",
                "pixel_format": "yuv420p",
                "tune": "fastdecode"
            },
            "audio": {
                "codec": "aac",
                "bitrate": "80k",
                "sample_rate": 44100,
                "channels": 2
            },
            "filters": ["-movflags", "+faststart"],  # 为Web优化
            "output_format": "mp4"
        },
        
        "custom": {
            "name": "自定义",
            "description": "完全自定义压缩参数",
            "icon": "🛠️",
            "compression_ratio": "可变",
            "use_case": "专业用户、特殊需求",
            "video": {
                "codec": "libx264",
                "crf": 23,
                "preset": "medium",
                "profile": "high",
                "level": "4.1",
                "pixel_format": "yuv420p",
                "tune": None
            },
            "audio": {
                "codec": "aac",
                "bitrate": "96k",
                "sample_rate": 44100,
                "channels": 2
            },
            "filters": [],
            "output_format": "mp4"
        }
    }
    
    # 分辨率预设
    RESOLUTION_PRESETS = {
        "original": {"name": "原始分辨率", "width": None, "height": None},
        "4k": {"name": "4K (3840x2160)", "width": 3840, "height": 2160},
        "1080p": {"name": "1080p (1920x1080)", "width": 1920, "height": 1080},
        "720p": {"name": "720p (1280x720)", "width": 1280, "height": 720},
        "480p": {"name": "480p (854x480)", "width": 854, "height": 480},
        "360p": {"name": "360p (640x360)", "width": 640, "height": 360}
    }
    
    # 帧率预设
    FRAMERATE_PRESETS = {
        "original": {"name": "原始帧率", "fps": None},
        "60": {"name": "60 FPS", "fps": 60},
        "30": {"name": "30 FPS", "fps": 30},
        "24": {"name": "24 FPS", "fps": 24},
        "15": {"name": "15 FPS", "fps": 15}
    }
    
    # 视频编码器选项
    VIDEO_CODECS = {
        "libx264": {
            "name": "H.264 (x264)",
            "description": "最广泛兼容的编码器",
            "quality": "高",
            "speed": "中等",
            "compatibility": "最佳"
        },
        "libx265": {
            "name": "H.265 (x265)",
            "description": "更高压缩比，较新的编码器",
            "quality": "非常高",
            "speed": "慢",
            "compatibility": "良好"
        },
        "libvpx-vp9": {
            "name": "VP9",
            "description": "Google开发的免费编码器",
            "quality": "高",
            "speed": "慢",
            "compatibility": "良好"
        }
    }
    
    # 音频编码器选项
    AUDIO_CODECS = {
        "aac": {
            "name": "AAC",
            "description": "标准音频编码器，广泛兼容",
            "quality": "高",
            "compatibility": "最佳"
        },
        "mp3": {
            "name": "MP3",
            "description": "经典音频格式",
            "quality": "中等",
            "compatibility": "最佳"
        },
        "opus": {
            "name": "Opus",
            "description": "高效的开源音频编码器",
            "quality": "非常高",
            "compatibility": "良好"
        }
    }
    
    @classmethod
    def get_preset(cls, preset_name: str) -> Dict[str, Any]:
        """获取指定的压缩预设"""
        return cls.PRESETS.get(preset_name, cls.PRESETS["standard"]).copy()
    
    @classmethod
    def get_all_presets(cls) -> Dict[str, Dict[str, Any]]:
        """获取所有压缩预设"""
        return cls.PRESETS.copy()
    
    @classmethod
    def get_preset_names(cls) -> List[str]:
        """获取所有预设名称"""
        return list(cls.PRESETS.keys())
    
    @classmethod
    def get_preset_display_info(cls, preset_name: str) -> Dict[str, str]:
        """获取预设的显示信息"""
        preset = cls.PRESETS.get(preset_name, cls.PRESETS["standard"])
        return {
            "name": preset["name"],
            "description": preset["description"],
            "icon": preset["icon"],
            "compression_ratio": preset["compression_ratio"],
            "use_case": preset["use_case"]
        }
    
    @classmethod
    def create_custom_preset(cls, name: str, video_params: Dict, audio_params: Dict, 
                           description: str = "自定义预设") -> Dict[str, Any]:
        """创建自定义预设"""
        custom_preset = cls.PRESETS["custom"].copy()
        custom_preset["name"] = name
        custom_preset["description"] = description
        custom_preset["video"].update(video_params)
        custom_preset["audio"].update(audio_params)
        return custom_preset
    
    @classmethod
    def validate_preset(cls, preset: Dict[str, Any]) -> bool:
        """验证预设配置的有效性"""
        required_keys = ["video", "audio", "output_format"]
        
        if not all(key in preset for key in required_keys):
            return False
        
        # 验证视频参数
        video_required = ["codec", "crf", "preset"]
        if not all(key in preset["video"] for key in video_required):
            return False
        
        # 验证音频参数
        audio_required = ["codec", "bitrate"]
        if not all(key in preset["audio"] for key in audio_required):
            return False
        
        return True
    
    @classmethod
    def get_ffmpeg_args(cls, preset: Dict[str, Any], input_file: str, output_file: str,
                       keep_audio: bool = True, custom_resolution: tuple = None,
                       custom_framerate: float = None) -> List[str]:
        """将预设转换为FFmpeg命令行参数"""
        args = ["-i", input_file]
        
        # 视频编码参数
        video_params = preset["video"]
        args.extend(["-c:v", video_params["codec"]])
        args.extend(["-crf", str(video_params["crf"])])
        args.extend(["-preset", video_params["preset"]])
        
        if video_params.get("profile"):
            args.extend(["-profile:v", video_params["profile"]])
        
        if video_params.get("level"):
            args.extend(["-level", video_params["level"]])
        
        if video_params.get("pixel_format"):
            args.extend(["-pix_fmt", video_params["pixel_format"]])
        
        if video_params.get("tune"):
            args.extend(["-tune", video_params["tune"]])
        
        # 分辨率设置
        if custom_resolution and custom_resolution[0] and custom_resolution[1]:
            args.extend(["-s", f"{custom_resolution[0]}x{custom_resolution[1]}"])
        
        # 帧率设置
        if custom_framerate:
            args.extend(["-r", str(custom_framerate)])
        
        # 音频编码参数
        if keep_audio:
            audio_params = preset["audio"]
            args.extend(["-c:a", audio_params["codec"]])
            args.extend(["-b:a", audio_params["bitrate"]])
            
            if audio_params.get("sample_rate"):
                args.extend(["-ar", str(audio_params["sample_rate"])])
            
            if audio_params.get("channels"):
                args.extend(["-ac", str(audio_params["channels"])])
        else:
            args.append("-an")  # 移除音频
        
        # 添加滤镜
        if preset.get("filters"):
            args.extend(preset["filters"])
        
        # 输出文件
        args.extend(["-y", output_file])  # -y 表示覆盖输出文件
        
        return args


# 全局预设管理器实例
compression_presets = CompressionPresets() 