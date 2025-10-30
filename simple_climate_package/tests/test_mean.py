import numpy as np
from pathlib import Path
import xarray as xr
import pytest

from simple_climate_package.mean import TempMean           # absolute import - run pytest from repo root
from simple_climate_package.tests.sample_data import make_sample_era5_tg


@pytest.fixture
def sample_tg_dataset():
    return make_sample_era5_tg()

# def test_mean()
    
def test_mean_anom(tmp_path: Path, sample_tg_dataset: xr.Dataset):
    # Save the in-memory dataset to a temporary NetCDF file
    file_path = tmp_path / "sample.nc"
    sample_tg_dataset.to_netcdf(file_path)
    print(sample_tg_dataset)

    # Create the TempExtremes object using the temp file (same as real code)
    te = TempMean(str(file_path), varname="tg")

    # choose start/end that are guaranteed to exist in the sample dataset
    start = np.datetime_as_string(sample_tg_dataset.time.min().values, unit='D')
    end   = np.datetime_as_string(sample_tg_dataset.time.max().values, unit='D')

    # call methods, pass a temp filename for the plots so they don't clutter repo
    mean_between = te.mean_between(start, end)
    mean_tot = te.mean_tot_time()
    mean_monthly = te.monthly_mean()
    mean_yearly = te.yearly_mean()
    clim_monthly = te.monthly_clim()
    clim_daily = te.daily_clim()
    anom_monthly = te.monthly_clim_Anom()
    anom_daily = te.daily_clim_Anom()

    # assertions: methods return floats and are in temp range 270-285
    for val in (mean_between, mean_tot, mean_monthly, mean_yearly,clim_daily, clim_monthly):
        assert isinstance(val, xr.DataArray)
        assert val.dtype == float or np.issubdtype(val.dtype, np.floating)
        assert ((val > 273.15) & (val < 283.15)).all()    
    
    for val in (anom_daily,anom_monthly):
        assert isinstance(val, xr.DataArray)
        assert val.dtype == float or np.issubdtype(val.dtype, np.floating)
        assert ((val > -10) & (val < 10)).all()    
