from setuptools import setup, find_packages

setup(
    name='py_auto_backup',
    version='1.1.0',
    packages=find_packages(),
    install_requires=[
        'rcon==2.4.4',
    ],
    author='Scott Canaga',
    url='https://github.com/blarggy/py_auto_backup'
)
