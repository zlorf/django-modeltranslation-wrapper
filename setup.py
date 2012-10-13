#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='django-modeltranslation-wrapper',
    description='Wrapper around modeltranslation package, adding nice features.',
    long_description=open('README.rst').read(),
    version='1.2',
    author='Jacek Tomaszewski',
    author_email='jacek.tomek@gmail.com',
    url='https://github.com/zlorf/django-modeltranslation-wrapper',
    license='BSD',
    install_requires=(
        'django-modeltranslation',
    ),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    packages=find_packages(),
    include_package_data = True,
)
