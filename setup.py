from distutils.core import setup
from setuptools import find_packages
from distutils.command.install import install as _install

setup(
  name = 'thunderscript',
  packages = find_packages(exclude=['config', 'config.*']),
  version = '16.10.08',
  description = 'Thunder script parser',
  author = 'Maciej Nabozny',
  author_email = 'maciej.nabozny@cloudover.io',
  url = 'http://cloudover.org/thunder/',
  download_url = 'https://github.com/cloudOver/thunder-script/archive/master.zip',
  keywords = ['corecluster', 'cloudover', 'cloud'],
  classifiers = [],
  install_requires = ['requests', 'pycore'],
)
