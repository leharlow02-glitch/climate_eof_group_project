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

## read data for analysis:
def read_data(data_path):
    Data = Dataset(data_path,mode='r')
    lons = Data.variables['longitude'][:]
    lats = Data.variables['latitude'][:]
    tg = Data.variables['tg'][:]
    tg_units = Data.variables['tg'].units
    print('shape of the Data:')
    print(tg.shape)
    print('units of ground temperature:')
    print(tg_units)
    print('printing Lon start and end:')
    print(lons[0])
    print(lons[-1])
    print('printing Lat start and end:')
    print(lats[0])
    print(lats[-1])
    

# read the data and make sure it works:
# data_path = input('Input the path to the data you want to analyse: ')
data_path = '/root/climate_eof_group_project/Data/Example_Data/e-obs_UK_ground_temp.nc'
check_nc_file(data_path)
read_data(data_path)
# Original path: '/root/Example_data/tg_ens_mean_0.25deg_reg_v30.0e.nc'
