import xarray as xr
import os
import sys
from netCDF4 import Dataset

def check_nc_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    try:
        ds = xr.open_dataset(file_path)
        print('\nThe data exists, go on with analysis :)')
        print(f"Opened: {file_path}")
        print("Dimensions:", ds.dims)
        print("Variables:", list(ds.data_vars))
        ds.close()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")


# read the data and make sure it works:
data_path = input('Input the path to the data you want to analyse: ')
check_nc_file(data_path)
# Original path: '/root/Example_data/tg_ens_mean_0.25deg_reg_v30.0e.nc'

