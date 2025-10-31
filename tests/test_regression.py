# tests/test_yearly_regression.py
import numpy as np
import pandas as pd
import xarray as xr
from numpy.testing import assert_allclose

from simple_climate_package.linear_regression import LinReg


# Making tests for linear regression class functions
def make_synthetic_daily_dataset(
    start="2000-01-01",
    end="2002-12-31",
    lat_vals=[0.0, 1.0],
    lon_vals=[0.0, 1.0],
):
    """
    Create a tiny synthetic daily Dataset with values = integer year
    shape: (time, lat, lon). This produces an exact slope = 1.0 (per year).
    """
    times = pd.date_range(start=start, end=end, freq="D")
    years = times.year.values.astype(float)
    T = len(times)
    ny = len(lat_vals)
    nx = len(lon_vals)

    # Create data with value equal to year across all grid points
    data = np.tile(years.reshape(T, 1, 1), (1, ny, nx))
    ds = xr.Dataset(
        {"tg": (("time", "lat", "lon"), data)},
        coords={"time": times, "lat": lat_vals, "lon": lon_vals},
    )
    return ds


def test_make_yearly_resamples_correctly(tmp_path):
    ds = make_synthetic_daily_dataset()
    p = tmp_path / "synthetic_daily.nc"
    ds.to_netcdf(p)

    lr = LinReg(str(p))
    annual = lr.make_yearly()
    expected_years = np.array([2000, 2001, 2002])
    got_years = annual["time"].dt.year.values
    assert_allclose(got_years, expected_years)

    # Yearly mean should equal that year
    # Check one grid cell (0,0)
    yearly_vals = annual.values[:, 0, 0]
    assert_allclose(yearly_vals, expected_years.astype(float))


def test_regress_yearly_recovers_slope_and_masks(tmp_path):
    # Create synthetic dataset
    ds = make_synthetic_daily_dataset()
    p = tmp_path / "synthetic_daily2.nc"
    ds.to_netcdf(p)

    lr = LinReg(str(p))
    lr.make_yearly()
    # Require all 3 years to be present
    res = lr.grid_linear_regression(min_obs=3)

    # Result should be an xarray.Dataset
    for v in [
        "slope",
        "per_decade",
        "p_value",
        "r2",
        "rmse",
        "n_obs",
        "intercept",
    ]:
        assert v in res.data_vars

    # Slope should be ~1.0 per year everywhere
    slope = res["slope"].values
    print(slope)
    # Allow tiny numerical tolerance
    assert_allclose(slope, np.ones_like(slope), atol=1e-12, rtol=0)

    # Per_decade should be ~10.0
    per_dec = res["per_decade"].values
    print(per_dec)
    assert_allclose(per_dec, 10.0 * np.ones_like(per_dec), atol=1e-11)

    # A case where one grid point has too few valid years
    ds2 = make_synthetic_daily_dataset()
    # Year 2001 to NaN for grid cell so it has only 2 valid years
    times = ds2["time"]
    mask_2001 = times.dt.year == 2001
    ds2["tg"].loc[dict(time=mask_2001, lat=0.0, lon=0.0)] = np.nan
    p2 = tmp_path / "synthetic_daily3.nc"
    ds2.to_netcdf(p2)

    lr2 = LinReg(str(p2))
    lr2.make_yearly()
    res2 = lr2.grid_linear_regression(min_obs=3)  # require 3 valid years

    # calculate slope for too few years
    slope2 = res2["slope"].values
    # Find index for lat=0.0, lon=0.0
    assert np.isnan(slope2[0, 0])

    # Another cell (0,1) should still have slope ~1
    assert_allclose(res2["slope"].values[0, 1], 1.0, atol=1e-12)
