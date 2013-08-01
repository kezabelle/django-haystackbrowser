# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

SHORT_DESC = (u'A reusable Django application for viewing and debugging '
                    u'all the data that has been pushed into Haystack')

REQUIREMENTS = [
    'Django>=1.2.0',
    'django-haystack>=1.2.0',
    'django-classy-tags>=0.3.4.1',
]

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
    version='0.4.0',
    description=SHORT_DESC,
    author='Keryn Knight',
    author_email='python-package@kerynknight.com',
    license="BSD License",
    keywords="django",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='https://github.com/kezabelle/django-haystackbrowser/tree/master',
    packages=PACKAGES,
    install_requires=REQUIREMENTS,
    classifiers=TROVE_CLASSIFIERS,
    platforms=['OS Independent'],
    package_data={'': [
        'templates/admin/haystackbrowser/*.html',
    ]},
)
