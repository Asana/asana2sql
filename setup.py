from setuptools import setup, find_packages

setup(name='asana2sql',
      version='0.1',
      description='Move data from Asana to SQL databases.',
      url='http://github.com/asana/asana2sql',
      author='Asana, Inc.',
      license='MIT',
      packages=find_packages(exclude="test"),
      install_requires=[])
