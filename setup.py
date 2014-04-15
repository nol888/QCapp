#!/usr/bin/env python3

import sys

from setuptools import setup, find_packages

setup(name="QCapp",
    version="0.0",
    description="QC application",
    author="",
    author_email="",
    url="",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'tornado'
    ],
    entry_points="""\
    [console_scripts]
    qcapp_server = qcapp:main
    """
    )