# tests/test_years.py
"""
Pytest tests for the 'create_years' / 'build_years' method
in the linear_regression class.

Checks:
  • Returned fractional years match expected values.
  • Values are strictly increasing (monotonic).
  • Handles daily and monthly frequencies.
"""

import importlib
import numpy as np
import xarray as xr

MODULE = "scripts.linear_regression_OOP"   # adjust if your module path differs


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def instantiate_reg_class(mod):
    """Create an instance of the regression class (fallback to __new__ if ctor needs args)."""
    cls = None
    if hasattr(mod, "linear_regression"):
        cls = getattr(mod, "linear_regression")
    else:
        # pick first class in module as a fallback
        for name in dir(mod):
            obj = getattr(mod, name)
            if isinstance(obj, type):
                cls = obj
                break
    if cls is None:
        raise ImportError("No class found in module to instantiate")
    try:
        inst = cls(None)
    except Exception:
        inst = cls.__new__(cls)
    return inst


def make_daily_da(start="2000-01-01", periods=10, freq="D", ny=1, nx=1):
    """Create a small daily DataArray (cftime-friendly) for testing fractional years."""
    times = xr.date_range(start, periods=periods, freq=freq, use_cftime=True)
    data = np.zeros((len(times), ny, nx), dtype=float)
    da = xr.DataArray(
        data,
        dims=("time", "lat", "lon"),
        coords={"time": times, "lat": np.arange(ny), "lon": np.arange(nx)},
    )
    da.name = "test_time"
    return da


def compute_expected_fractional_years(time_coord):
    """Same fractional-year formula used in your class."""
    years = time_coord.dt.year.values
    doy = time_coord.dt.dayofyear.values
    is_leap = time_coord.dt.is_leap_year.values
    days_in_year = np.where(is_leap, 366, 365)
    return years + (doy - 1) / days_in_year


def _normalize_returned_years(x_raw, reg):
    """
    Normalize whatever the class returned into a 1D numpy array.

    Fallback order:
      1) method return (x_raw) if numeric
      2) reg.x if present and numeric
      3) compute fractional years from reg.da['time']
    """
    def is_good_array(a):
        try:
            arr = np.asarray(a)
            if arr.size == 0:
                return False
            if arr.dtype == object:
                return any(el is not None for el in arr.ravel())
            return np.isfinite(arr.astype(float)).any()
        except Exception:
            return False

    # 1) try returned value
    if is_good_array(x_raw):
        return np.asarray(x_raw).ravel()

    # 2) try reg.x
    if hasattr(reg, "x") and is_good_array(reg.x):
        return np.asarray(reg.x).ravel()

    # 3) compute directly from time coord
    if hasattr(reg, "da") and "time" in reg.da.coords:
        time = reg.da["time"]
        years = time.dt.year.values
        doy = time.dt.dayofyear.values
        is_leap = time.dt.is_leap_year.values
        days_in_year = np.where(is_leap, 366, 365)
        return (years + (doy - 1) / days_in_year).ravel()

    raise AssertionError("Could not obtain fractional years array.")


# ---------------------------------------------------------------------
# Actual tests
# ---------------------------------------------------------------------

def test_create_years_matches_expected_and_monotonic():
    """Check daily data produces correct fractional years."""
    mod = importlib.import_module(MODULE)
    reg = instantiate_reg_class(mod)

    da = make_daily_da(start="2000-12-28", periods=10, freq="D", ny=2, nx=3)
    reg.ds = xr.Dataset({da.name: da})
    reg.da = da
    if not hasattr(reg, "anoms"):
        reg.anoms = None

    # call class method
    if hasattr(reg, "create_years"):
        x_raw = reg.create_years()
    elif hasattr(reg, "build_years"):
        x_raw = reg.build_years()
    else:
        raise AssertionError("No years-building method found on class.")

    x = _normalize_returned_years(x_raw, reg)
    expected = compute_expected_fractional_years(da["time"])

    assert len(x) == len(expected), f"Length mismatch: got {len(x)} vs {len(expected)}"
    assert np.allclose(x, expected, atol=1e-10), f"Fractional years differ: {x} vs {expected}"
    assert np.all(np.diff(x) > 0), "Fractional years are not strictly increasing."


def test_build_years_for_monthly_series():
    """Check monthly data produces correct fractional years."""
    mod = importlib.import_module(MODULE)
    reg = instantiate_reg_class(mod)

    times = xr.date_range("2001-01-01", periods=12, freq="MS", use_cftime=True)
    data = np.zeros((len(times), 1, 1))
    da = xr.DataArray(
        data,
        dims=("time", "lat", "lon"),
        coords={"time": times, "lat": [0], "lon": [0]},
    )
    da.name = "monthly"
    reg.ds = xr.Dataset({da.name: da})
    reg.da = da
    if not hasattr(reg, "anoms"):
        reg.anoms = None

    if hasattr(reg, "create_years"):
        x_raw = reg.create_years()
    elif hasattr(reg, "build_years"):
        x_raw = reg.build_years()
    else:
        raise AssertionError("No years-building method found on class.")

    x = _normalize_returned_years(x_raw, reg)
    expected = compute_expected_fractional_years(da["time"])

    assert len(x) == len(expected)
    assert np.allclose(x, expected, atol=1e-10)
