# tests/test_anomalies.py
import numpy as np
import xarray as xr
import importlib
import pytest

MODULE = "scripts.linear_regression_OOP"   

def make_monthly_dummy_dataset(start="2000-01-01", end="2001-12-31", ny=2, nx=3):
    """Create monthly DataArray where value at each time = month number (1..12)."""
    # create times as date_time dates (xarray helper); works in environments that use date_time
    times = xr.date_range(start, end, freq="MS")
    # extract month numbers directly from date_time objects
    months = np.array([t.month for t in times], dtype=int)

    # broadcast months into spatial grid (time, lat, lon)
    data = np.repeat(months[:, None, None], ny * nx).reshape(len(months), ny, nx).astype(float)

    da = xr.DataArray(data,
                      dims=("time", "lat", "lon"),
                      coords={"time": times, "lat": np.arange(ny), "lon": np.arange(nx)})
    da.name = "testvar"
    return da


def instantiate_reg_class(mod):
    """
    Try to get the regression class from module:
    prefer 'linear_regression', else any class defined there.
    Return an instance with .ds and .da set up ready to call methods.
    """
    cls = None
    if hasattr(mod, "linear_regression"):
        cls = getattr(mod, "linear_regression")
    else:
        # pick the first class object defined in module (fallback)
        for objname in dir(mod):
            obj = getattr(mod, objname)
            if isinstance(obj, type):
                cls = obj
                break
    if cls is None:
        raise ImportError("No class found in module to instantiate")

    # Try normal construction; if it requires args, create blank and set attributes
    try:
        inst = cls(None)   # try calling with None (your __init__ may accept path)
    except Exception:
        inst = cls.__new__(cls)
    return inst

def test_compute_monthly_anoms_zero_monthly_mean():
    # import module
    mod = importlib.import_module(MODULE)

    da = make_monthly_dummy_dataset()  # monthly values equal to month number
    reg = instantiate_reg_class(mod)

    # attach dataset & dataarray in case __init__ didn't do it
    ds = xr.Dataset({da.name: da})
    # prefer attributes used in prior code: .ds and .da
    reg.ds = ds
    reg.da = da

    # call the method: try common names / signatures
    if hasattr(reg, "compute_monthly_anoms"):
        # some implementations accept a baseline tuple; pass a sensible baseline
        res = reg.compute_monthly_anoms(baseline=("2000-01-01", "2001-12-31"))
    elif hasattr(reg, "compute_anomalies"):
        res = reg.compute_anomalies(da, baseline=("2000-01-01", "2001-12-31"), method="monthly")
    else:
        pytest.skip("No anomaly method found on class")

    # Ensure we got an xarray.DataArray back
    assert isinstance(res, xr.DataArray)

    # Group by month and check means ~= 0
    month_means = res.groupby("time.month").mean("time")
    # every month mean should be near zero (floating rounding tolerance)
    assert np.allclose(month_means.values, 0.0, atol=1e-12), f"monthly means not zero: {month_means.values}"
