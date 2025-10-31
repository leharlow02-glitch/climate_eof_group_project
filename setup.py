from setuptools import setup, find_packages
import io


def get_version():
    """
    Safely obtain VERSION from simple_climate_package/version_info.py without importing
    the package. Executes that single file in a small namespace and reads VERSION.
    Validates the version string using packaging.version.
    """
    import re
    from pathlib import Path

    version_file = Path(__file__).parent / "simple_climate_package" / "version_info.py"
    if not version_file.exists():
        raise RuntimeError(f"version_info.py not found at {version_file}")
    code = version_file.read_text(encoding="utf8")

    # Execute the file in a restricted namespace to capture variables (safe for static files)
    ns: dict = {}
    try:
        exec(compile(code, str(version_file), "exec"), {}, ns)
    except Exception as e:
        raise RuntimeError(f"Failed to execute version_info.py: {e!r}")

    # Try to get VERSION
    version = ns.get("VERSION")
    if version is None:
        # Fallback: try to parse a literal tuple or VERSION_INT if present
        # e.g. VERSION_INT = 1, 0, 0
        m = re.search(r"^VERSION_INT\s*=\s*(.+)$", code, re.M)
        if m:
            try:
                # Evaluate the tuple expression safely using ast.literal_eval
                import ast
                version_int = ast.literal_eval(m.group(1))
                version = ".".join(str(int(x)) for x in version_int)
            except Exception:
                pass

    if not version:
        raise RuntimeError("Unable to determine VERSION from simple_climate_package/version_info.py")

    # Validate the version string is PEP 440 compatible
    try:
        from packaging.version import Version as _V
        _V(str(version))
    except Exception as e:
        raise RuntimeError(f"Invalid version string from version_info.py: {version!r}: {e}")

    return str(version)



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
    version="1.0.0",
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
