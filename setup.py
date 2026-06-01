"""PyLevelator setup."""

from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy
import sys

if sys.platform == 'win32':
    extra_compile_args = ['/O2', '/openmp']
    extra_link_args = []
elif sys.platform == 'darwin':
    extra_compile_args = ['-O3', '-fopenmp']
    extra_link_args = ['-fopenmp']
else:
    extra_compile_args = ['-O3', '-fopenmp']
    extra_link_args = ['-fopenmp']

extensions = [
    Extension(
        "pylevelator.core_cython_optimized",
        ["pylevelator/core_cython_optimized.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "pylevelator.core_cython",
        ["pylevelator/core_cython.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
]

setup(
    packages=find_packages(include=["pylevelator", "pylevelator.*"]),
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
        }
    ),
    zip_safe=False,
)
