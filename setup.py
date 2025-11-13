"""Setup script for the organize package"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text() if readme_file.exists() else ''

setup(
    name='florg',
    version='1.0.0',
    author='Laísa Rio',
    description='A CLI tool for batch file renaming and organizing',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/laisario/florg',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'click>=8.1.0',
        'rich>=13.0.0',
        'questionary>=2.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'organize=organize.cli:organize',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='file organizer renamer batch cli',
)


