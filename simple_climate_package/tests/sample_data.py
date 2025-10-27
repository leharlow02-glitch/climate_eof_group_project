import xarray as xr
import numpy as np
import pandas as pd

def make_sample_era5_t2m():
    # make a sample ERA5 t2m dataset
    # our code expects the same coordinate structure of time, latitude, longitude, t2m
    # this dataset keeps to the expected coordinate structure:
    # times gives daily timestamps
    times = pd.date_range("2020-01-01", "2021-12-31", freq="D")
    # lats gives 3 grid points between -10 and 10
    lons = np.linspace(100, 110, 3)
    # lons gives 3 grid points between 100 and 110
    lats = np.linspace(-10, 10, 3)
    # data generates synthetic temperature data for every timestamp, latitude, and longitude
    # multiplying by 10 and then adding 273.15 gives a range of 0-10 degrees celcius
    data = 273.15 + 10*np.random.rand(len(times), len(lons), len(lats))

    # this wraps the created data into an xarray dataset
    ds = xr.Dataset(
        {"t2m": (("time", "longitude", "latitude"), data)},
        coords={"time": times, "longitude": lons, "latitude": lats},
        attrs={"description": "Synthetic ERA5-like temperature dataset (for tests)"}
    )
    return ds
