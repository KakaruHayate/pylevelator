"""Build configuration for the PyLevelator Cython extension."""

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
import sys

if sys.platform == 'win32':
    extra_compile_args = ['/O2', '/openmp']
    extra_link_args = []
elif sys.platform == 'darwin':
    extra_compile_args = ['-O3', '-Xpreprocessor', '-fopenmp']
    extra_link_args = ['-lomp']
else:
    extra_compile_args = ['-O3', '-fopenmp']
    extra_link_args = ['-fopenmp']

extensions = [
    Extension(
        "pylevelator._cython_impl",
        ["pylevelator/_cython_impl.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
        }
    ),
)
