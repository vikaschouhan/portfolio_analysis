from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

setup(
    ext_modules=cythonize("numpy_ext.pyx", build_dir="/tmp/.build"),
    include_dirs=[numpy.get_include()]
)    
