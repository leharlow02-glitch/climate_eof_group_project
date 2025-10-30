# Simple_climate_package

The open-source Python package **simple_climate_package** reads in netcdf data from E-OBS, performs simple statistical tests and visualises the outputs. 

Statistical tests included in this package:
- Minimum values
- Maximum values
- Mean values
- Climate anomaly values
- Linear regression

# Table of Contents
1. Installation
2. Usage
3. Features
4. Contributions
5. License

# 1. Installation
## Installing without a virtual environment

For general use of this package without a virtual environment, please import using pip install.

```bash 
pip install simple_climate_package
```


## Installation using a virtual environment

To ensure the use of the same packages and dependencies, please follow these steps when setting up your local environment. This method is preferred for developers.

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

## Installing data

This package was developed to work with E-OBS daily gridded mean temperature data from 1950 to present. 

A sample dataset for data over The United Kingdom from 1950 to present can be found in the Data folder located in the simple_climate_package folder.

To use your own data, please copy this code into a script.

```python
import cdsapi

dataset = "insitu-gridded-observations-europe"
request = {
    "product_type": "ensemble_mean",
    "variable": ["mean_temperature"],
    "grid_resolution": "0_25deg",
    "period": "full_period",
    "version": ["30_0e"]
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()
```

# 3. Features



# 4. Authors & Contributions

This package was created by [Hannah-Jane Wood](https://github.com/hannahw0od), [Lucy Harlow](https://github.com/leharlow02-glitch), and [Ofer Cohen](https://github.com/ofer-cohen)

# 5. License
The simple_climate_package is licensed under the [MIT License](LICENSE) - see the LICENSE file for details