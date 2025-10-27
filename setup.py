#
# pkmodel setuptools script
#
from setuptools import setup, find_packages


def get_version():
    """
    Get version number from the simple_climate_package module.
    """
    import os
    import sys

    sys.path.append(os.path.abspath('simple_climate_package'))
    from simple_climate_package.version_info import VERSION as version
    sys.path.pop()
    return version


def get_readme():
    """
    Load README.md text for use as description.
    """
    with open('README.md') as f:
        return f.read()


# Go!
setup(
    # Module name (lowercase)
    name='simple_climate_package',

    # Version
    version=get_version(),
    description='An example Python project.',
    long_description=get_readme(),
    license='MIT license',
    author='Hannah-Jane Wood, Lucy Harlow, Ofer Cohen',
    author_email='lucy.harlow@reuben.ox.ac.uk',
    maintainer='Martin Robinson',
    maintainer_email='martin.robinson@cs.ox.ac.uk',
    url='https://github.com/leharlow02-glitch/climate_eof_group_project',
    # Packages to include
    packages=find_packages(include=('simple_climate_package', 'simple_climate_package.*')),
    # List of dependencies
    extras_require={
        'docs': [
            # Sphinx for doc generation. Version 1.7.3 has a bug:
            'sphinx>=1.5, !=1.7.3',
            # Nice theme for docs
            'sphinx_rtd_theme',
        ],
        'dev': [
            # Flake8 for code style checking
            'flake8>=3',
            'pytest',
            'build'
        ],
    },
    python_requires='>=3.8',
)