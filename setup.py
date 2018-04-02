"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='django_namedtuples',
    description='Django namedtuples queryset',

    author='Konstantin Gukov',
    author_email='gukkos@gmail.com',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.0.0',
    url='https://github.com/yavia/django-namedtuples',
    download_url='https://github.com/yavia/django-namedtuples/archive/1.0.0.tar.gz',

    license='GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Framework :: Django :: 1.8',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='django queryset namedtuple',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['django_namedtuples'],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['enum34', 'Django>=1.7.0', 'Django<1.9'],
)