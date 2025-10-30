from pathlib import Path

import numpy as np
import pytest
import xarray as xr
from extremes import (
    TempExtremes,
)  # absolute import - run pytest from repo root
from tests.sample_data import make_sample_era5_tg


@pytest.fixture
def sample_tg_dataset():
    return make_sample_era5_tg()


def test_temp_extremes_with_tempfile(
    tmp_path: Path, sample_tg_dataset: xr.Dataset
):
    # Save the in-memory dataset to a temporary NetCDF file
    file_path = tmp_path / "sample.nc"
    sample_tg_dataset.to_netcdf(file_path)

    # Create the TempExtremes object using the temp file (same as real code)
    te = TempExtremes(str(file_path), varname="tg")

    # choose start/end that are guaranteed to exist in the sample dataset
    start = np.datetime_as_string(
        sample_tg_dataset.time.min().values, unit="D"
    )
    end = np.datetime_as_string(sample_tg_dataset.time.max().values, unit="D")

    # call methods, pass a temp filename for
    # the plots so they don't clutter repo
    min_val = te.min_between(start, end, save_as=str(tmp_path / "min.png"))
    max_val = te.max_between(start, end, save_as=str(tmp_path / "max.png"))
    min_tot = te.min_tot(save_as=str(tmp_path / "min_tot.png"))
    max_tot = te.max_tot(save_as=str(tmp_path / "max_tot.png"))
    #monthly_min = te.monthly_min()
    #monthly_max = te.monthly_max()
    yearly_min = te.yearly_min()
    yearly_max = te.yearly_max()

    # assertions: methods return floats and are in temp range 270-285
    for val in (min_val, max_val, min_tot, max_tot):
        assert isinstance(val, float)
        assert 270 < val < 285

    # assertions: methods return xarray with float values in temp range 270-285
    for val in (yearly_min, yearly_max):
        assert isinstance(val, xr.DataArray)
        assert val.dtype == float or np.issubdtype(val.dtype, np.floating)
        assert ((val > 270) & (val < 285)).all()
