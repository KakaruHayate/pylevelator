"""
PyLevelator - 现代化的 Python 音频均衡工具

基于原始 Levelator 算法的优化 Cython 实现
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
import sys
from pathlib import Path

# 读取 README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

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
    Extension(
        "pylevelator.core_cython_optimized",
        ["core_cython_optimized.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
]

setup(
    name="pylevelator",
    version="1.1.0",
    author="KakaruHayate",
    author_email="",
    description="现代化的 Python 音频均衡工具 - 比原版 Levelator 快 40%",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KakaruHayate/pylevelator",
    project_urls={
        "Bug Tracker": "https://github.com/KakaruHayate/pylevelator/issues",
        "Documentation": "https://github.com/KakaruHayate/pylevelator#readme",
        "Source Code": "https://github.com/KakaruHayate/pylevelator",
    },

    packages=["pylevelator"],
    package_dir={"pylevelator": "."},

    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
        }
    ),

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Editors",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Cython",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],

    python_requires=">=3.8",

    install_requires=[
        'numpy>=1.19.0',
        'soundfile>=0.12.0',
    ],

    extras_require={
        "dev": [
            "cython>=0.29.0",
            "pytest>=6.0",
            "build>=0.7.0",
            "twine>=3.4.0",
        ],
    },

    keywords=[
        "audio",
        "levelator",
        "audio-processing",
        "audio-normalization",
        "audio-leveling",
        "cython",
        "performance",
    ],

    zip_safe=False,
)
