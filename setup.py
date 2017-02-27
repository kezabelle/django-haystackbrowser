# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
if sys.version_info[0] == 2:
    # get the Py3K compatible `encoding=` for opening files.
    from io import open


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
            with open(filepath, mode='r', encoding="utf-8") as f:
                yield f.read()


HERE = os.path.abspath(os.path.dirname(__file__))
SHORT_DESC = """A reusable Django application for viewing and debugging all the data that has been pushed into Haystack"""
LONG_DESCRIPTION = "\r\n\r\n----\r\n\r\n".join(make_readme(HERE))


TROVE_CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Natural Language :: English',
    'Topic :: Internet :: WWW/HTTP :: Site Management',
    'Topic :: Database :: Front-Ends',
    'License :: OSI Approved :: BSD License',
    'Framework :: Django',
    'Framework :: Django :: 1.4',
    'Framework :: Django :: 1.5',
    'Framework :: Django :: 1.6',
    'Framework :: Django :: 1.7',
    'Framework :: Django :: 1.8',
]

PACKAGES = find_packages()

setup(
    name='django-haystackbrowser',
    version='0.6.2',
    description=SHORT_DESC,
    author='Keryn Knight',
    author_email='python-package@kerynknight.com',
    license="BSD License",
    keywords="django",
    zip_safe=False,
    long_description=LONG_DESCRIPTION,
    url='https://github.com/kezabelle/django-haystackbrowser/tree/master',
    packages=PACKAGES,
    install_requires=[
        'django-classy-tags>=0.3.4.1',
        # as of now, django-haystack's latest version is 2.5.0, and explicitly
        # doesn't support Django 1.10+
        # So, we put this last, to ensure that it pegs the maximum version
        # where packages with looser requirements may say otherwise.
        'django-haystack>=1.2.0',
    ],
    tests_require=[
        'pytest==2.9.2',
        'pytest-cov==2.2.1',
        'pytest-django==2.9.1',
        'pytest-mock==1.1',
        'pytest-remove-stale-bytecode==2.1',
        'Whoosh',
    ],
    cmdclass={'test': PyTest, 'tox': Tox},
    classifiers=TROVE_CLASSIFIERS,
    platforms=['OS Independent'],
    package_data={'': [
        'templates/admin/haystackbrowser/*.html',
    ]},
)
