import numpy as np

def test_mean(sample_t2m_dataset):
    ds = sample_t2m_dataset
    yearly_mean = ds["t2m"].groupby("time.year").mean("time")

    #checking correctness:

    # there should be 1 mean per year
    assert set(yearly_mean.year.values) == {2020,2021}

    # the mean should be within reasonable temperature bounds
    assert np.all((yearly_mean.values > 270) & (yearly_mean.values < 285))

    # the structure should match expected dimensions
    assert yearly_mean.dims == ("year", "latitude", "longitude")
