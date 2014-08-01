from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys
from schemazoid import __version__


class PyTest(TestCommand):
    """Command class to allow `setup.py test` to run py.test.

    http://pytest.org/latest/goodpractises.html#integration-with-setuptools-distribute-test-commands
    """
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


with open('README.rst') as thefile:
    README = thefile.read()

setup(
    name="schemazoid",
    version=__version__,
    packages=find_packages(),
    author="Vince Veselosky",
    author_email="vince@veselosky.com",
    description="A lightweight data modeling framework for Python",
    long_description=README,
    url="https://github.com/veselosky/schemazoid",

    install_requires=[
        'python-dateutil',
        'pytz',
        'six',
    ],
    tests_require=[
        'pytest',
    ],
    cmdclass={'test': PyTest},

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
)
