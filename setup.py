import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "PySpeedup",
    version = "0.1.2.2",
    author = "Chris Dusold",
    author_email = "PySpeedup@ChrisDusold.com",
    description = ("A multiprocess framework for efficient calculations."),
    license = read("LICENSE"),
    keywords = "algorithmic speedup framework",
    url = "http://pyspeedup.rtfd.org/",
    packages=['pyspeedup', 'pyspeedup.concurrent', 'pyspeedup.algorithms', 'pyspeedup.memory', 'tests'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent", #Hopefully.
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: System :: Hardware :: Symmetric Multi-processing",
        "Topic :: Utilities",
    ],
)
