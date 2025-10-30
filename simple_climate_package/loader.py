## 
from dataclasses import dataclass
import xarray as xr
import os
from typing import Optional, Dict

@dataclass
class DataReader:
    filepath: str                     # file path or glob pattern
    use_mfdataset: bool = False       # set True if path is a glob / many files
    chunks: Optional[Dict] = None     # e.g. {"time": 100} to enable dask lazy loading
    def __init__(self,filepath):
        self.filepath = filepath
        
    def read(self) -> xr.Dataset:
        if not os.path.exists(self.filepath) and not self.use_mfdataset:
            raise FileNotFoundError(f"File not found: {self.filepath}")

        if self.use_mfdataset:
            ds = xr.open_mfdataset(self.filepath, combine="by_coords",
                                   decode_times=True, chunks=self.chunks)
        else:
            ds = xr.open_dataset(self.filepath, decode_times=True, chunks=self.chunks)

        return ds


# # simple_climate_package/loader.py
# from __future__ import annotations
# from typing import Optional, Union
# from pathlib import Path
# import xarray as xr

# class DatasetLoader:
#     """
#     Responsible for opening a NetCDF / Zarr dataset in a safe, configurable way.

#     Parameters
#     ----------
#     chunks : dict | None
#         Chunking to pass to xarray.open_dataset. If None, dataset is opened eagerly
#         (no dask). Example: {'time': 365} or {'time': 100, 'latitude': 50, 'longitude': 50}.
#     decode_times : bool
#         Whether to decode times on open. Default True.
#     verbose : bool
#         If True, log information about the opened dataset (dimensions, variables).
#     """

#     def __init__(self, chunks: Optional[dict] = None, decode_times: bool = True):
#         self.chunks = chunks
#         self.decode_times = decode_times
#         self._ds: Optional[xr.Dataset] = None
#         self._source: Optional[Union[str, Path, xr.Dataset]] = None

#     def open(self, source: Union[str, Path, xr.Dataset]) -> xr.Dataset:
#         """
#         Open and return an xarray.Dataset (cached).

#         Parameters
#         ----------
#         source : str | Path | xr.Dataset
#             File path, URL, or an already-open xarray.Dataset. If an xarray.Dataset is passed,
#             it is returned unchanged (but stored in the loader cache).
#         """
#         # If it's already an xarray Dataset, just store & return it
#         if isinstance(source, xr.Dataset):
#             self._source = source
#             self._ds = source
#             return self._ds

#         # normalize to Path / str
#         path = Path(source)
#         self._source = str(path)

#         # check existence early (helpful for local paths)
#         if not path.exists():
#             raise FileNotFoundError(f"File not found: {path}")

#         # If already opened the same source, return cached
#         if self._ds is not None and getattr(self._ds, "encoding", {}).get("source") == str(path):
#             return self._ds

#         try:
#             # Use xarray.open_dataset with provided chunking and decode_times options.
#             # When chunks is not None, xarray will return a dask-backed dataset (lazy).
#             self._ds = xr.open_dataset(str(path), chunks=self.chunks, decode_times=self.decode_times)
#         except Exception as exc:
#             raise RuntimeError(f"Error reading {path}: {exc}") from exc

#         return self._ds

#     def open_variable(self, source: Union[str, Path, xr.Dataset], varname: str = 'tg') -> xr.DataArray:
#         """
#         Open dataset and return a single DataArray for `varname`. Raises KeyError if variable missing.
#         """
#         ds = self.open(source)
#         if varname not in ds:
#             raise KeyError(f"Variable '{varname}' not found in dataset. Available: {list(ds.data_vars)}")
#         return ds[varname]
