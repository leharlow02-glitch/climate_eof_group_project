from simple_climate_package.mean import CalcMean           # absolute import - run pytest from repo root
from simple_climate_package.extremes import CalcExtremes
from simple_climate_package.linear_regression import linear_regression
import xarray as xr
import matplotlib.pyplot as plt
import os
import pandas as pd


print('Example data for the UK can be found here on the github repository: /root/climate_eof_group_project/Data/Example_Data/e-obs_UK_ground_temp.nc' )
data_path = input('Input the path to the data you want to analyse: ')

tm = CalcMean(data_path)
'''print(tm.mean_between('1950-01-01', '1955-01-01'))'''
tm.plot_mean_tot_time()
tm.plot_monthly_climatology()
tm.plot_mean_between('1950-01-01', '1955-01-01')
tm.plot_yearly_mean()
month_clim = tm.monthly_clim()
print(month_clim.shape)
clim_amon = tm.monthly_clim_Anom()
print(clim_amon.shape)
day_clim = tm.daily_clim()
print(day_clim.shape)
daily_amon = tm.daily_clim_Anom()
print(daily_amon.shape)


tx = CalcExtremes(data_path)
tx.plot_max_between('1950-01-01', '1955-01-01')
tx.plot_max_tot()
tx.plot_min_between('1950-01-01', '1955-01-01')
tx.plot_min_tot()
tx.plot_yearly_max()
tx.plot_yearly_min()

tl = linear_regression(data_path)
tl.quick_plot_signif_stippling()