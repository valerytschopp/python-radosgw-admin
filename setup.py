import os
import sys

# export DISTUTILS_DEBUG=1

try:
    from setuptools import setup
    setup
except ImportError:
    from distutils.core import setup

setup(
    name='radosgw-admin',
    version='1.7.2',
    author='Valery Tschopp',
    author_email='valery.tschopp@gmail.com',
    include_package_data=True,
    requires=['boto'],
    install_requires=['boto'],
    packages=['radosgw'],
    url='https://github.com/valerytschopp/python-radosgw-admin',
    license='GPLv3',
    description='Ceph RADOS Gateway (rgw) admin operations REST API',
    long_description=open('README.rst').read(),
    #test_suite='tests'
)
