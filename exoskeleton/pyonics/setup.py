from setuptools import setup, find_packages
import klampt
import numpy
import matplotlib
import matplotlib.pyplot
import pandas
import submodules.apps
import submodules.video
import submodules.audio
import submodules.control
import submodules.ui
import submodules.network


setup(
    name='pyonics',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[klampt,
                      numpy,
                      matplotlib,
                      pandas

        # List your dependencies here
    ],
)