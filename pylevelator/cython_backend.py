"""
Cython 后端实现
"""

import numpy as np
import wave
from pathlib import Path
from typing import Union, Optional, Callable

try:
    from pylevelator.core_cython import (
        calculate_rms_envelope_fast,
        calculate_gain_curve_fast,
        smooth_gains_fast,
        apply_gains_fast,
        apply_lookahead_limiter_fast
    )
    CYTHON_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False


class CythonBackend:
    """Cython 优化后端"""

    def __init__(self, target_rms=0.12, window_size=0.5, smoothing=0.3,
                 max_gain=20.0, min_gain=-10.0, lookahead=0.1):
        """
        初始化 Cython 后端

        Args:
            target_rms: 目标 RMS
            window_size: 窗口大小（秒）
            smoothing: 平滑系数
            max_gain: 最大增益 (dB)
            min_gain: 最小增益 (dB)
            lookahead: 前瞻时间（秒）
        """
        self.target_rms = target_rms
        self.window_size = window_size
        self.smoothing = smoothing
        self.max_gain = max_gain
        self.min_gain = min_gain
        self.lookahead = lookahead

    def read_wav(self, filename):
        """读取 WAV 文件"""
        with wave.open(str(filename), 'rb') as wav:
            params = wav.getparams()
            nchannels, sampwidth, framerate, nframes = params[:4]
            frames = wav.readframes(nframes)

            if sampwidth == 3:
                audio_bytes = np.frombuffer(frames, dtype=np.uint8)
                audio_bytes = audio_bytes.reshape(-1, 3)
                audio = (audio_bytes[:, 0].astype(np.int32) |
                        (audio_bytes[:, 1].astype(np.int32) << 8) |
                        (audio_bytes[:, 2].astype(np.int32) << 16))
                audio = np.where(audio >= 0x800000, audio - 0x1000000, audio)
                audio = audio.astype(np.float32) / 8388608.0
            elif sampwidth == 2:
                audio = np.frombuffer(frames, dtype=np.int16)
                audio = audio.astype(np.float32) / 32768.0
            else:
                raise ValueError(f"不支持的采样宽度: {sampwidth}")

            if nchannels > 1:
                audio = audio.reshape(-1, nchannels)

            return audio, framerate, nchannels, sampwidth

    def write_wav(self, filename, audio, framerate, nchannels, sampwidth):
        """写入 WAV 文件"""
        if sampwidth == 3:
            audio_int = np.clip(audio * 8388608.0, -8388608, 8388607).astype(np.int32)
            audio_bytes = np.zeros((len(audio_int), 3), dtype=np.uint8)
            audio_bytes[:, 0] = audio_int & 0xFF
            audio_bytes[:, 1] = (audio_int >> 8) & 0xFF
            audio_bytes[:, 2] = (audio_int >> 16) & 0xFF
            audio_int = audio_bytes.flatten()
        elif sampwidth == 2:
            audio_int = np.clip(audio * 32768.0, -32768, 32767).astype(np.int16)

        with wave.open(str(filename), 'wb') as wav:
            wav.setnchannels(nchannels)
            wav.setsampwidth(sampwidth)
            wav.setframerate(framerate)
            wav.writeframes(audio_int.tobytes())

    def process(self, input_file: Union[str, Path], output_file: Optional[Union[str, Path]] = None,
                progress_callback: Optional[Callable[[str, int], None]] = None,
                timeout: Optional[int] = None) -> Path:
        """处理音频文件"""
        if not CYTHON_AVAILABLE:
            raise RuntimeError("Cython 后端不可用，请先编译: python setup.py build_ext --inplace")

        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        if output_file is None:
            output_path = input_path.parent / f"{input_path.stem}.output{input_path.suffix}"
        else:
            output_path = Path(output_file)

        filename = input_path.name

        # 读取音频
        if progress_callback:
            progress_callback(filename, 5)

        audio, framerate, nchannels, sampwidth = self.read_wav(input_path)

        # 转为单声道处理
        if len(audio.shape) > 1:
            audio_mono = np.mean(audio, axis=1).astype(np.float32)
        else:
            audio_mono = audio.astype(np.float32)

        if progress_callback:
            progress_callback(filename, 10)

        # 计算 RMS 包络
        window_samples = int(self.window_size * framerate)
        hop_samples = window_samples // 4

        rms_values = calculate_rms_envelope_fast(audio_mono, window_samples, hop_samples)

        if progress_callback:
            progress_callback(filename, 40)

        # 插值回原始长度
        rms_envelope = np.interp(
            np.arange(len(audio_mono)),
            np.arange(len(rms_values)) * hop_samples + window_samples // 2,
            rms_values
        ).astype(np.float32)

        # 计算增益曲线
        gain_curve = calculate_gain_curve_fast(
            rms_envelope,
            self.target_rms,
            self.max_gain,
            self.min_gain
        )

        if progress_callback:
            progress_callback(filename, 60)

        # 平滑增益
        smoothing_samples = int(self.smoothing * framerate)
        if smoothing_samples > 1:
            gain_curve = smooth_gains_fast(gain_curve, smoothing_samples)

        if progress_callback:
            progress_callback(filename, 75)

        # 前瞻限幅
        lookahead_samples = int(self.lookahead * framerate)
        if lookahead_samples > 0:
            gain_curve = apply_lookahead_limiter_fast(
                audio_mono,
                gain_curve,
                lookahead_samples,
                0.98
            )

        if progress_callback:
            progress_callback(filename, 90)

        # 应用增益
        if len(audio.shape) > 1:
            # 多声道：对每个声道应用相同的增益
            audio_processed = np.zeros_like(audio)
            for ch in range(audio.shape[1]):
                audio_processed[:, ch] = apply_gains_fast(audio[:, ch].astype(np.float32), gain_curve)
        else:
            audio_processed = apply_gains_fast(audio_mono, gain_curve)

        # 写入
        self.write_wav(output_path, audio_processed, framerate, nchannels, sampwidth)

        if progress_callback:
            progress_callback(filename, 100)

        return output_path

    def is_available(self) -> bool:
        """检查后端是否可用"""
        return CYTHON_AVAILABLE

    def get_info(self) -> dict:
        """获取后端信息"""
        return {
            'name': 'Cython',
            'description': 'Cython 优化实现',
            'available': CYTHON_AVAILABLE,
            'accuracy': '95-99%',
            'speed': 'Fast (10-30s for 30s audio)',
            'platform': 'All',
        }
