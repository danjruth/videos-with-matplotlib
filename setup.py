from setuptools import setup, find_packages

setup(name='videos-with-matplotlib',
      version='0.1',
      packages=find_packages(),
      author='Daniel J. Ruth',
      url=r'hhttps://github.com/danjruth/videos-with-matplotlib',
      description='Easily create videos with matplotlib',
      long_description=open('README.md').read(),
      install_requires=[
          'matplotlib',
          'numpy',
          'scipy',
          ],
      )