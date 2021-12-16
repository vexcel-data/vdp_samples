"""
A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject

Based on this: https://github.com/pypa/sampleproject/blob/main/setup.py
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name='vdp_python_tools',  
    version='0.0.0',  
    description='A python module for working with WMTS map tiles', 
    packages=[
        "vdp_python_tools", # that's the code in ./vdp_python_tools
        ],
)