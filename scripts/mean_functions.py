import xarray as xr
import os
import sys
from netCDF4 import Dataset
import matplotlib.pyplot as plt

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
    ds = xr.open_dataset(data_path)
    print('\nOverview:')
    print(ds)
    print('\nVariables:')
    print(ds.variables)     # List of variables
    print('\nCoordinates:')
    print(ds.coords)        # Coordinate variables
    return ds


def plot_time_mean(ds, var="tg", out_path="/root/climate_eof_group_project/plots/time_mean.png"):
    """Compute mean of `var` over time and save plot to `out_path`."""
    temp_mean = calculate_time_mean(ds)
    plt.figure()
    ax = temp_mean.plot()
    plt.title(f"Mean {var} from {ds.time.min().values} to {ds.time.max().values}")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()  # good practice in scripts
    print(f"Plot saved to: {out_path}")

# def plot_time_mean():
#     temp_mean = calculate_time_mean(ds)
#     print(temp_mean.shape)
#     print(temp_mean)
#     temp_mean.plot()
#     plt.title('mean ground temperature from 1/1/1950 to 30/06/2024')
#     # plt.show()
#     plt.savefig("temp_mean.png", dpi=150, bbox_inches="tight")
#     print("Plot saved to temp_mean.png")

def calculate_time_mean(ds):
    return ds["tg"].mean(dim="time")

print('Example data for the UK can be found here on the github repository: /root/climate_eof_group_project/Data/Example_Data/e-obs_UK_ground_temp.nc' )
data_path = input('Input the path to the data you want to analyse: ')

check_nc_file(data_path)
ds = read_data(data_path)
plot_time_mean(ds)