# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

"""
Levelator 核心算法 - Cython 优化版本

高性能的音频处理核心，使用 Cython 编译为 C 扩展
"""

cimport numpy as np
import numpy as np
from libc.math cimport sqrt, log10, pow as c_pow
from libc.stdlib cimport malloc, free

ctypedef np.float32_t DTYPE_t


cpdef np.ndarray[DTYPE_t, ndim=1] calculate_rms_envelope_fast(
    np.ndarray[DTYPE_t, ndim=1] audio,
    int window_size,
    int hop_size
):
    """
    快速 RMS 包络计算

    使用滑动窗口计算 RMS，Cython 优化版本
    预期加速: 20-50x

    Args:
        audio: 音频数据
        window_size: 窗口大小（样本数）
        hop_size: 跳跃大小（样本数）

    Returns:
        RMS 值数组
    """
    cdef int i, j, start, end
    cdef float sum_sq
    cdef int audio_len = len(audio)
    cdef int num_windows = (audio_len - window_size) // hop_size + 1
    cdef np.ndarray[DTYPE_t, ndim=1] rms_values = np.zeros(num_windows, dtype=np.float32)

    # 计算每个窗口的 RMS
    for i in range(num_windows):
        start = i * hop_size
        end = start + window_size
        if end > audio_len:
            end = audio_len

        sum_sq = 0.0
        for j in range(start, end):
            sum_sq += audio[j] * audio[j]

        rms_values[i] = sqrt(sum_sq / (end - start))

    return rms_values


cpdef np.ndarray[DTYPE_t, ndim=1] calculate_gain_curve_fast(
    np.ndarray[DTYPE_t, ndim=1] rms_envelope,
    float target_rms,
    float max_gain_db,
    float min_gain_db
):
    """
    快速增益曲线计算

    根据 RMS 包络计算所需增益
    预期加速: 10-20x

    Args:
        rms_envelope: RMS 包络
        target_rms: 目标 RMS
        max_gain_db: 最大增益 (dB)
        min_gain_db: 最小增益 (dB)

    Returns:
        线性增益数组
    """
    cdef int i
    cdef float target_db, current_db, gain_db
    cdef int n = len(rms_envelope)
    cdef np.ndarray[DTYPE_t, ndim=1] gain_linear = np.zeros(n, dtype=np.float32)

    target_db = 20.0 * log10(target_rms)

    for i in range(n):
        # 避免除零
        if rms_envelope[i] < 1e-8:
            rms_envelope[i] = 1e-8

        current_db = 20.0 * log10(rms_envelope[i])
        gain_db = target_db - current_db

        # 限制增益范围
        if gain_db > max_gain_db:
            gain_db = max_gain_db
        elif gain_db < min_gain_db:
            gain_db = min_gain_db

        # 转换为线性增益
        gain_linear[i] = c_pow(10.0, gain_db / 20.0)

    return gain_linear


cpdef np.ndarray[DTYPE_t, ndim=1] smooth_gains_fast(
    np.ndarray[DTYPE_t, ndim=1] gains,
    int kernel_size
):
    """
    快速增益平滑

    使用移动平均平滑增益曲线
    预期加速: 5-10x

    Args:
        gains: 增益数组
        kernel_size: 平滑窗口大小

    Returns:
        平滑后的增益数组
    """
    cdef int i, j, start, end
    cdef float sum_val
    cdef int n = len(gains)
    cdef np.ndarray[DTYPE_t, ndim=1] smoothed = np.zeros(n, dtype=np.float32)
    cdef int half_kernel = kernel_size // 2

    for i in range(n):
        start = max(0, i - half_kernel)
        end = min(n, i + half_kernel + 1)

        sum_val = 0.0
        for j in range(start, end):
            sum_val += gains[j]

        smoothed[i] = sum_val / (end - start)

    return smoothed


cpdef np.ndarray[DTYPE_t, ndim=1] apply_gains_fast(
    np.ndarray[DTYPE_t, ndim=1] audio,
    np.ndarray[DTYPE_t, ndim=1] gains
):
    """
    快速应用增益

    将增益应用到音频并限幅
    预期加速: 5-10x

    Args:
        audio: 音频数据
        gains: 增益数组

    Returns:
        处理后的音频
    """
    cdef int i
    cdef int n = len(audio)
    cdef np.ndarray[DTYPE_t, ndim=1] result = np.zeros(n, dtype=np.float32)
    cdef float sample

    for i in range(n):
        sample = audio[i] * gains[i]

        # 限幅
        if sample > 0.99:
            sample = 0.99
        elif sample < -0.99:
            sample = -0.99

        result[i] = sample

    return result


cpdef np.ndarray[DTYPE_t, ndim=1] apply_lookahead_limiter_fast(
    np.ndarray[DTYPE_t, ndim=1] audio,
    np.ndarray[DTYPE_t, ndim=1] gains,
    int lookahead_samples,
    float max_allowed
):
    """
    快速前瞻限幅器

    防止削波的前瞻限幅
    预期加速: 10-20x

    Args:
        audio: 音频数据
        gains: 增益数组
        lookahead_samples: 前瞻样本数
        max_allowed: 最大允许值

    Returns:
        限制后的增益数组
    """
    cdef int i, j
    cdef int n = len(audio)
    cdef np.ndarray[DTYPE_t, ndim=1] limited_gains = gains.copy()
    cdef float predicted_peak, reduction

    for i in range(n):
        predicted_peak = abs(audio[i]) * gains[i]

        if predicted_peak > max_allowed:
            reduction = max_allowed / predicted_peak

            # 向前传播限制
            for j in range(max(0, i - lookahead_samples), i + 1):
                if limited_gains[j] > reduction:
                    limited_gains[j] = reduction

    return limited_gains
