# Standard library imports.
import os

# Third-party imports.
from setuptools import find_packages, setup

__author__ = 'Jason Parent'

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    readme = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-foodie',
    version='0.0.3',
    description='An app for foodies.',
    long_description=readme,
    author='Jason Parent',
    author_email='jason.a.parent@gmail.com',
    url='https://github.com/ParentJA/django-foodie',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['django<1.10', 'djangorestframework>3,<4'],
    license='Apache Software License 2.0',
    zip_safe=False,
    keywords='django-foodie',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
