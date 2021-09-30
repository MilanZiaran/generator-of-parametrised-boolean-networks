from setuptools import setup, find_packages

setup(
    name='parametrised_bn_gen',
    version='0.1',
    description='Generator of parametrised boolean networks',
    packages=find_packages(),
    install_requires=['networkx', 'numpy', 'tk']
)
