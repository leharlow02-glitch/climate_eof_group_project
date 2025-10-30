from setuptools import setup, find_packages
import io


def get_version():
    # Read VERSION from simple_climate_package/version_info.py without importing package
    import re
    from pathlib import Path

    init_path = Path(__file__).parent / "simple_climate_package" / "version_info.py"
    if not init_path.exists():
        raise RuntimeError(f"version_info.py not found at {init_path}")
    text = init_path.read_text(encoding="utf8")
    m = re.search(r"^VERSION\s*=\s*['\"]([^'\"]+)['\"]", text, re.M)
    if m:
        return m.group(1)
    raise RuntimeError("Unable to find VERSION in simple_climate_package/version_info.py")



def get_readme():
    # Load README.md text for use as description.
    with open('README.md') as f:
        return f.read()

def parse_requirements(filename):
    # Read a requirements file and return a list suitable for install_requires.
    # Ignores comments, editable installs (-e) and vcs/git lines.

    reqs = []
    with io.open(filename, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # ignore editable installs and VCS links which aren't valid in install_requires
            if line.startswith("-e") or line.startswith("git+") or "://" in line:
                continue
            reqs.append(line)
    return reqs

# Go!
setup(
    # Module name (lowercase)
    name='simple_climate_package',

    # Version
    version=get_version(),
    description='Simple statistical analysis for E-OBS datasets',
    long_description=get_readme(),
    license='MIT license',
    author='Hannah-Jane Wood, Lucy Harlow, Ofer Cohen',
    author_email='lucy.harlow@reuben.ox.ac.uk',
    url='https://github.com/leharlow02-glitch/climate_eof_group_project',
    # Packages to include
    packages=find_packages(
        include=('simple_climate_package', 'simple_climate_package.*')),
    # Runtime dependencies (read from requirements.txt)
    install_requires=parse_requirements("requirements.txt"),
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
    python_requires='>=3.11',
)
