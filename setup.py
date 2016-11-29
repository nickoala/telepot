from setuptools import setup
from setuptools.command.install_lib import install_lib
from setuptools.command.build_py import build_py
from os import path
import sys
import re

def _not_async(filepath):
    return filepath.find('aio/') < 0

# Do not copy async module for Python 3.3 or below.
class nocopy_async(build_py):
    def find_all_modules(self):
        modules = build_py.find_all_modules(self)
        modules = list(filter(lambda m: _not_async(m[-1]), modules))
        return modules

    def find_package_modules(self, package, package_dir):
        modules = build_py.find_package_modules(self, package, package_dir)
        modules = list(filter(lambda m: _not_async(m[-1]), modules))
        return modules

# Do not compile async.py for Python 3.3 or below.
class nocompile_async(install_lib):
    def byte_compile(self, files):
        files = list(filter(_not_async, files))
        install_lib.byte_compile(self, files)


PY_35 = sys.version_info >= (3,5)

here = path.abspath(path.dirname(__file__))

install_requires = ['urllib3>=1.9.1']
cmdclass = {}

if PY_35:
    # one more dependency for Python 3.5 (async version)
    install_requires += ['aiohttp>=0.21.6']
else:
    # do not copy/compile async version for older Python
    cmdclass['build_py'] = nocopy_async
    cmdclass['install_lib'] = nocompile_async


try:
    # read pypi.rst for long_description
    with open(path.join(here, 'pypi.rst')) as f:
        long_description = f.read()
except:
    long_description = ''


# Parse version
with open(path.join(here, 'telepot', '__init__.py')) as f:
    m = re.search('^__version_info__ *= *\(([0-9]+), *([0-9]+)\)', f.read(), re.MULTILINE)
    version = '.'.join(m.groups())


setup(
    cmdclass=cmdclass,

    name='telepot',
    packages=['telepot', 'telepot.aio'],
    # Do not filter out packages because we need the whole thing during `sdist`.

    install_requires=install_requires,

    version=version,

    description='Python framework for Telegram Bot API',

    long_description=long_description,

    url='https://github.com/nickoala/telepot',

    author='Nick Lee',
    author_email='lee1nick@yahoo.ca',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='telegram bot api python wrapper',
)
