"""
Cython 版本的 setup.py
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "core_cython",
        ["core_cython.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=['-O3'],  # 优化标志
    )
]

setup(
    name="pylevelator-cython",
    version="1.0.0",
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
    ],
)
