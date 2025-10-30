import xarray as xr
import numpy as np
import pandas as pd


def make_sample_era5_tg():
    times = pd.date_range("2020-01-01", "2021-12-31", freq="D")
    lons = np.linspace(100, 110, 3)
    lats = np.linspace(-10, 10, 3)
    data = 273.15 + (10 * np.random.rand(len(times), len(lons), len(lats)))
    ds = xr.Dataset(
        {"tg": (("time", "longitude", "latitude"), data)},
        coords={"time": times, "longitude": lons, "latitude": lats},
        attrs={"description": "Synthetic ERA5-like temperature dataset"}
    )
    return ds

sample_data = make_sample_era5_tg();
print(sample_data.data_vars)

