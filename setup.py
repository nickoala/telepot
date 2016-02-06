from setuptools import setup
from setuptools.command.install_lib import install_lib
from setuptools.command.build_py import build_py
from os import path
import sys

def _not_async(filepath):
    return filepath.find('async/') < 0

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


PY_34 = sys.version_info >= (3,4)

here = path.abspath(path.dirname(__file__))

install_requires = ['requests>=2.4.0']
cmdclass = {}

if PY_34:
    # one more dependency for Python 3.4
    install_requires += ['aiohttp']
else:
    # do not copy/compile async module for Python 3.3 or below
    cmdclass['build_py'] = nocopy_async
    cmdclass['install_lib'] = nocompile_async


try:
    # read pypi.rst for long_description
    with open(path.join(here, 'pypi.rst')) as f:
        long_description = f.read()
except:
    long_description = ''


setup(
    cmdclass=cmdclass,

    name='telepot',
    packages=['telepot', 'telepot.async'],
    # Do not filter out packages because we need the whole thing during `sdist`.

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=install_requires,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='6.3',

    description='Python framework for Telegram Bot API',

    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/nickoala/telepot',

    # Author details
    author='Nick Lee',
    author_email='lee1nick@yahoo.ca',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='telegram bot api python wrapper',
)
