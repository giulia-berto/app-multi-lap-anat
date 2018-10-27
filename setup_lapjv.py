from distutils.core import setup, Extension
import numpy

setup(
    ext_modules = [
    	Extension("linear_assignment",["linear_assignment.c"],
    			include_dirs=[numpy.get_include()]),
    ],
)
