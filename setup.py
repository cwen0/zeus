# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='zeus',
    version='0.0.1',
    author="cwen",
    author_email="yincwengo@gmail.com",

    packages=[
        "zeus",
        "zeus.datasource",
        "zeus.models",
        "zeus.libs",
    ],
    include_package_data=True,
    platforms="any",
    install_requires=[
        'scikit-learn',
        'numpy',
        'pandas',
        'requests',
        'tornado',
        'slackclient',
    ],
)
