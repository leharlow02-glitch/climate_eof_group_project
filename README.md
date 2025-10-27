# Simple_climate_package

A simple climate analysis package that reads in netcdf data from E-Obs, performs simple statistical tests (see below) and visualises the outputs. 

Statistical tests included in this package:
- Linear regression
- Minimum values
- Maximum values
- EOF analysis 

# Setting up your Python virtual environment

To ensure the use of the same packages and dependencies, please follow these steps when setting up your local environment.

These commands are for bash. 

### Step 1: Clone the repository
```bash
git clone <repo_url>
cd <repo_name>
```

### Step 2: Create and activate a virtual environment
```bash
python3 -m venv env
source env/bin/activate
```

### Step 3: Install dependencies from virtual_environment_requirements.txt
```bash 
pip install -r virtual_environment_requirements.txt
```

