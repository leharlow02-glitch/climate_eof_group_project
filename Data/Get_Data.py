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
        print(f"\nOpened: {file_path}")
        print("Dimensions:", ds.dims)
        print("Variables:", list(ds.data_vars))
        ds.close()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")


check_nc_file('/root/Example_data/mean_temperature.nc')

# if __name__ == "__main__":
    
    
