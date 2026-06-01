"""
PyLevelator - 现代化的 Python 音频均衡工具
"""

__version__ = "1.1.0"

from pylevelator.optimized_backend import OptimizedBackend
from pylevelator.cython_backend import CythonBackend

Levelator = OptimizedBackend

__all__ = ["Levelator", "OptimizedBackend", "CythonBackend", "__version__"]
