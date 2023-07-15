import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.1.3'

setup(
    license='MIT',
    name="devoid_client",
    version=VERSION,
    author="Devoid AI",
    author_email="<devoidai@proton.me>",
    description="Client for Devoid AI Image generator",
    url='https://devoid.pics',
    packages=find_packages(exclude=['tests', 'tests.']),
    install_requires=['requests', 'setuptools', 'websockets']
)