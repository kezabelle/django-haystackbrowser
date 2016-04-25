# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


def make_readme(root_path):
    consider_files = ('README.rst', 'LICENSE', 'CHANGELOG', 'CONTRIBUTORS')
    for filename in consider_files:
        filepath = os.path.realpath(os.path.join(root_path, filename))
        if os.path.isfile(filepath):
            with open(filepath, mode='r') as f:
                yield f.read()


HERE = os.path.abspath(os.path.dirname(__file__))
SHORT_DESC = """A reusable Django application for viewing and debugging
all the data that has been pushed into Haystack"""
LONG_DESCRIPTION = "\r\n\r\n----\r\n\r\n".join(make_readme(HERE))


TROVE_CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Natural Language :: English',
    'Topic :: Internet :: WWW/HTTP :: Site Management',
    'Topic :: Database :: Front-Ends',
    'License :: OSI Approved :: BSD License',
]

PACKAGES = find_packages()

setup(
    name='django-haystackbrowser',
    version='0.6.1',
    description=SHORT_DESC,
    author='Keryn Knight',
    author_email='python-package@kerynknight.com',
    license="BSD License",
    keywords="django",
    zip_safe=False,
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='https://github.com/kezabelle/django-haystackbrowser/tree/master',
    packages=PACKAGES,
    install_requires=[
        'Django>=1.3.1',
        'django-haystack>=1.2.0',
        'django-classy-tags>=0.3.4.1',
    ],
    tests_require=[
        'django-haystack>=1.2.0',
        'pytest>=2.6.4',
        'pytest-cov>=1.8.1',
        'pytest-django>=2.8.0',
        'pytest-mock>=0.11.0',
        'pytest-remove-stale-bytecode>=1.0',
    ],
    cmdclass={'test': PyTest, 'tox': Tox},
    classifiers=TROVE_CLASSIFIERS,
    platforms=['OS Independent'],
    package_data={'': [
        'templates/admin/haystackbrowser/*.html',
    ]},
)
