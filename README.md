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
2. Features
3. Contributions
4. License

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

# 2. Features
An example analysis script using **simple_climate_package** is listed in the github repository.
Start by specifying the path to you data file.
The data path is an input to many of our methods, so is useful to specify at the beginning of your analysis.

```python
data_path = input('Input the path to the data you want to analyse: ')
```

## Calculating the mean
To conduct analysis using mean data, import the class CalcMean from **simple_climate_package**.
Input the path to your data file into CalcMean and label this as 'tm'.
'tm' is your temperature instance and what will be used to conduct your analysis.

```python
from simple_climate_package.mean import CalcMean


tm = CalcMean(data_path)
```

To obtain the dataset of the mean temperature data for each grid pixel over the entire timeseries, call **mean_tot_time()**.

```python
mean_tot = tm.mean_tot_time()
```

A visualisation of the mean temperature over the entire timeseries can be called using **plot_mean_tot_time()**.

```python
tm.plot_mean_tot_time()
```

This method saves a plot to a filepath specified in the arguement of the method.

![Screenshot](./plots/mean_time_tot_tg.png)

Note that **mean_tot_time()** does not need to be called to use **plot_mean_tot_time()**.

Instead of getting the total mean, you can specify the dates between which you want to calculate the mean.

```python
mean_between = tm.mean_between(start_date, end_date)
tm.plot_mean_between(start_date, end_date)
```

To get a dataset for the mean temperature of every grid pixel per year, call **yearly_mean()**.
Calling **plot_yearly_mean()** creates a plot of the mean temperature for every year in the dataset.

```python
yearly_mean = tm.yearly_mean()
tm.plot_yearly_mean()
```
For studying monthly climatology (monthly trends over the entire timeseries), call **monthly_clim()**.
**Monthly_clim()** returns a dataset with 12 values (one per month) representing the long-term monthly climatology.
Calling **tm.plot_monthly_climatology()** plots the climatology for each month.

```python
month_clim = tm.monthly_clim()
tm.plot_monthly_climatology()
```

![Screenshot](./plots/monthly_clim/mean_tg_for_Apr.png)

Instead of monthly trends, daily climatology (daily trends over the entire timeseries) can be calculating by calling **daily_clim**.
There is not a plotting function for daily climatology due to the large volume of days in the dataset.

```python
day_clim = tm.daily_clim()
```

Climatology is used to calculate the climate anomaly.
The monthly climate anomaly, calculated by subtracting the long-term monthly climatology from the monthly mean, is called using **monthly_clim_Anom()**.
**Monthly_clim_Anom()** provides a dataset for climate anomaly of every month in the dataset.
The daily climate anomaly, calculated by subtracting the long-term daily climatology from the temperature for each day in the data, is called using **daily_climate_Anom()**

```python
clim_anom = tm.monthly_clim_Anom()
daily_anom = tm.daily_clim_Anom()
```

Climate anomalies are not plotted in this package but can be used for further analysis such as fair comparison of global trends.

## Calculating extreme values
To conduct analysis using minimum or maximum data, import the class CalcExtremes from **simple_climate_package**.
Input the path to your data file into CalcExtremes and label this as 'tx'.
'tx' is your temperature instance and what will be used to conduct your analysis.

```python
from simple_climate_package.mean import CalcExtremes


tx = CalcExtremes(data_path)
```
To obtain the dataset of the minimum temperature data for each grid pixel over the entire timeseries, call **min_tot()**.
To obtain the dataset of the maximum temperature data for each grid pixel over the entire timeseries, call **max_tot()**.

```python
min_tot = tx.min_tot()
max_tot = tx.max_tot()
```

A visualisation of the minimum or maximum temperature over the entire timeseries can be called using **plot_min_tot()** or **plot_max_tot()** respectively.

```python
tx.plot_min_tot()
tx.plot_max_tot()
```

This method saves a plot to a filepath specified in the arguement of the method.

![Screenshot](./plots/yearly_max/max_tg_for_1950.png)

Note that **min_tot_time()** and **max_tot_time()** do not need to be called to use **plot_min_tot()** and **plot_max_tot()** respectively.

Instead of getting the total minimum/maximum value, you can specify the dates between which you want to calculate it.

```python
min_between = tx.min_between(start_date, end_date)
tx.plot_min_between(start_date, end_date)
max_between = tx.max_between(start_date, end_date)
tx.plot_max_between(start_date, end_date)
```

To get a dataset for the minimum or maximum temperature of every grid pixel per year, call **yearly_min()** or **yearly_max()** respectively.
Calling **plot_yearly_min()** or **plot_yearly_max()** creates a plot of the minimum or maximum temperature for every year in the dataset.

```python
yearly_min = tx.yearly_min()
tx.plot_yearly_min()
yearly_max = tx.yearly_max()
tx.plot_yearly_max()
```

## Linear Regression
To conduct analysis using linear regression data, import the class LinReg from **simple_climate_package**.
Input the path to your data file into LinReg and label this as 'tl'.
'tl' is your temperature instance and what will be used to conduct your analysis.

```python
from simple_climate_package.linear_regression import LinReg


tl = LinReg(data_path)
```

Calling **grid_linear_regression** calculates the linear regression for each grid pixel in the entire dataset.

```python
lin_reg = tl.grid_linear_regression()
```

Note that the dataset is resampled from daily to yearly means for efficiency.
This method takes yearly mean as imports and returns arrays of variables.

Variables returned: slope, intercept, t_stat, p_value, r2, rmse, n_obs, per_decade, total_change

These variables can be used for further analysis.
Calling **quick_plot_signif_stippling()** plots the temperature's change per decade

```python
tl.quick_plot_signif_stippling()
```

![Screenshot](./plots/linear_regression_of_tg.png)

# 3. Authors & Contributions

This package was created by [Hannah-Jane Wood](https://github.com/hannahw0od), [Lucy Harlow](https://github.com/leharlow02-glitch), and [Ofer Cohen](https://github.com/ofer-cohen)

# 4. License
The simple_climate_package is licensed under the [MIT License](LICENSE) - see the LICENSE file for details