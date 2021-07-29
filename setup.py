#!/usr/bin/env python
# coding=utf-8


from setuptools import setup
from src import __version__

setup(
    name='namecheap-dns-manager',
    version=__version__,
    author='fangwentong',
    author_email='fangwentong2012@gmail.com',
    license='MIT',
    packages=['namecheap_dns_manager'],
    package_dir={"namecheap_dns_manager":"src"},
    zip_safe=False,
    include_package_data=True,
    entry_points={
        'console_scripts': ['namecheap-dns-manager=namecheap_dns_manager.dns_cli:main']
    },
    install_requires=['PyNamecheap==0.0.3', 'PyYAML==5.4']
)
