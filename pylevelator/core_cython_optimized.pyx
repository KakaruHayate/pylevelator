# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

"""
Levelator 核心算法 - 优化版本

使用 OpenMP 并行化 + 优化的内存访问
"""

cimport numpy as np
import numpy as np
from libc.math cimport sqrt, log10, pow as c_pow
from cython.parallel import prange

ctypedef np.float32_t DTYPE_t


cpdef np.ndarray[DTYPE_t, ndim=1] calculate_rms_envelope_fast(
    np.ndarray[DTYPE_t, ndim=1] audio,
    int window_size,
    int hop_size
):
    """
    快速 RMS 包络计算 - 并行化版本

    使用 OpenMP 并行计算多个窗口
    """
    cdef int i, j, start, end
    cdef float sum_sq
    cdef int audio_len = len(audio)
    cdef int num_windows = (audio_len - window_size) // hop_size + 1
    cdef np.ndarray[DTYPE_t, ndim=1] rms_values = np.zeros(num_windows, dtype=np.float32)
    cdef float[:] audio_view = audio
    cdef float[:] rms_view = rms_values

    # 并行计算每个窗口的 RMS
    for i in prange(num_windows, nogil=True, schedule='static'):
        start = i * hop_size
        end = start + window_size
        if end > audio_len:
            end = audio_len

        sum_sq = 0.0
        for j in range(start, end):
            sum_sq = sum_sq + audio_view[j] * audio_view[j]

        rms_view[i] = sqrt(sum_sq / <float>(end - start))

    return rms_values


cpdef np.ndarray[DTYPE_t, ndim=1] calculate_gain_curve_fast(
    np.ndarray[DTYPE_t, ndim=1] rms_envelope,
    float target_rms,
    float max_gain_db,
    float min_gain_db
):
    """
    快速增益曲线计算 - 并行化版本
    """
    cdef int i
    cdef float target_db, current_db, gain_db
    cdef int n = len(rms_envelope)
    cdef np.ndarray[DTYPE_t, ndim=1] gain_linear = np.zeros(n, dtype=np.float32)
    cdef float[:] rms_view = rms_envelope
    cdef float[:] gain_view = gain_linear

    target_db = 20.0 * log10(target_rms)

    # 并行计算增益
    for i in prange(n, nogil=True, schedule='static'):
        # 避免除零
        if rms_view[i] < 1e-8:
            rms_view[i] = 1e-8

        current_db = 20.0 * log10(rms_view[i])
        gain_db = target_db - current_db

        # 限制增益范围
        if gain_db > max_gain_db:
            gain_db = max_gain_db
        elif gain_db < min_gain_db:
            gain_db = min_gain_db

        # 转换为线性增益
        gain_view[i] = c_pow(10.0, gain_db / 20.0)

    return gain_linear


cpdef np.ndarray[DTYPE_t, ndim=1] smooth_gains_fast(
    np.ndarray[DTYPE_t, ndim=1] gains,
    int kernel_size
):
    """
    快速增益平滑 - 并行化版本
    """
    cdef int i, j, start, end
    cdef float sum_val
    cdef int n = len(gains)
    cdef np.ndarray[DTYPE_t, ndim=1] smoothed = np.zeros(n, dtype=np.float32)
    cdef int half_kernel = kernel_size // 2
    cdef float[:] gains_view = gains
    cdef float[:] smoothed_view = smoothed

    # 并行平滑
    for i in prange(n, nogil=True, schedule='static'):
        start = max(0, i - half_kernel)
        end = min(n, i + half_kernel + 1)

        sum_val = 0.0
        for j in range(start, end):
            sum_val = sum_val + gains_view[j]

        smoothed_view[i] = sum_val / <float>(end - start)

    return smoothed


cpdef np.ndarray[DTYPE_t, ndim=1] apply_gains_fast(
    np.ndarray[DTYPE_t, ndim=1] audio,
    np.ndarray[DTYPE_t, ndim=1] gains
):
    """
    快速应用增益 - 并行化版本
    """
    cdef int i
    cdef int n = len(audio)
    cdef np.ndarray[DTYPE_t, ndim=1] result = np.zeros(n, dtype=np.float32)
    cdef float sample
    cdef float[:] audio_view = audio
    cdef float[:] gains_view = gains
    cdef float[:] result_view = result

    # 并行应用增益
    for i in prange(n, nogil=True, schedule='static'):
        sample = audio_view[i] * gains_view[i]

        # 限幅
        if sample > 0.99:
            sample = 0.99
        elif sample < -0.99:
            sample = -0.99

        result_view[i] = sample

    return result


cpdef np.ndarray[DTYPE_t, ndim=1] apply_lookahead_limiter_fast(
    np.ndarray[DTYPE_t, ndim=1] audio,
    np.ndarray[DTYPE_t, ndim=1] gains,
    int lookahead_samples,
    float max_allowed
):
    """
    快速前瞻限幅器

    注意：这个函数不能完全并行化，因为有依赖关系
    """
    cdef int i, j
    cdef int n = len(audio)
    cdef np.ndarray[DTYPE_t, ndim=1] limited_gains = gains.copy()
    cdef float predicted_peak, reduction
    cdef float[:] audio_view = audio
    cdef float[:] gains_view = gains
    cdef float[:] limited_view = limited_gains

    # 这部分需要串行处理（有依赖）
    for i in range(n):
        predicted_peak = abs(audio_view[i]) * gains_view[i]

        if predicted_peak > max_allowed:
            reduction = max_allowed / predicted_peak

            # 向前传播限制
            for j in range(max(0, i - lookahead_samples), i + 1):
                if limited_view[j] > reduction:
                    limited_view[j] = reduction

    return limited_gains
