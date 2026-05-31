"""
优化版 setup.py

添加 OpenMP 支持
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
import sys

# OpenMP 编译标志
if sys.platform == 'win32':
    extra_compile_args = ['/O2', '/openmp']
    extra_link_args = []
elif sys.platform == 'darwin':
    # macOS 使用 libomp
    extra_compile_args = ['-O3', '-fopenmp']
    extra_link_args = ['-fopenmp']
else:
    # Linux
    extra_compile_args = ['-O3', '-fopenmp']
    extra_link_args = ['-fopenmp']

extensions = [
    # 原版（无并行化）
    Extension(
        "core_cython",
        ["core_cython.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=['-O3'] if sys.platform != 'win32' else ['/O2'],
    ),
    # 优化版（并行化）
    Extension(
        "core_cython_optimized",
        ["core_cython_optimized.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
]

setup(
    name="pylevelator",
    version="1.1.0",
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
        }
    ),
    install_requires=[
        'numpy>=1.19.0',
        'cython>=0.29.0',
        'soundfile>=0.12.0',
    ],
)
