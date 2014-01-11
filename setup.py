import os
from setuptools import setup
import smopy

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="smopy",
    version=smopy.__version__,
    author="Cyrille Rossant",
    author_email="rossant@github",
    description=(("OpenStreetMap image tiles in Python")),
    license="BSD",
    keywords="openstreetmap matplotlib map maps ipython",
    url="http://packages.python.org/smopy",
    py_modules=['smopy'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Framework :: IPython",
        "License :: OSI Approved :: BSD License",
    ],
)

