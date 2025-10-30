"""simple_climate_package is a Climate analysis library.

It contains functionality for downloading, analysing, and plotting
temperature data over Europe
"""
# Import version info
from .version_info import VERSION_INT, VERSION  # noqa

# Import main classes
# simple_climate_package/__init__.py
from .mean import CalcMean
from .extremes import CalcExtremes
from .loader import DataReader
from .linear_regression import LinReg
__all__ = ["CalcMean", "CalcExtremes",'DataReader']
__version__ = "0.1.0"   # or import from _version.py
