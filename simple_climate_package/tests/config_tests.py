import pytest
from tests.sample_data import make_sample_era5_t2m

@pytest.fixture
def sample_t2m_dataset():
    # this fixture creates a small synthetic ERA5 dataset in memory
    return make_sample_era5_t2m()