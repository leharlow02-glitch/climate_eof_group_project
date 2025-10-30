import os

import matplotlib.pyplot as plt
import xarray as xr


class TempExtremes:
    def __init__(self, filepath, varname="tg"):

        # check the file exists
        if not os.path.exists(filepath):
            FileNotFoundError(f"File not found: {filepath}")

        # try to open the dataset
        try:
            self.ds = xr.open_dataset(filepath, decode_times=True)
            print("\nThe data exists, go on with analysis :)")
            print(f"Opened: {filepath}")
            print("Dimensions:", self.ds.dims)
            print("Variables:", list(self.ds.data_vars))

            # store the temperature variable
            self.tg = self.ds[varname]

        except Exception as e:
            raise RuntimeError(f"Error reading {filepath}: {e}")

    def min_between(self, start, end, save_as="min.png"):
        # Identify the minimum temperature values between two dates and plot

        # select data between two dates
        selected_data = self.tg.sel(time=slice(start, end))

        # plot this data on a map
        min_map = selected_data.min(dim="time")
        qm = min_map.plot()  # xarray returns an Axes object
        ax = qm.axes
        ax.set_title(f"Minimum temperature values between {start} and {end}")
        ax.figure.savefig(save_as, bbox_inches="tight")
        plt.close(ax.figure)

        return float(selected_data.min())

    def max_between(self, start, end, save_as="max.png"):
        # Identify the maximum temperature values between two dates and plot

        # select data between two dates
        selected_data = self.tg.sel(time=slice(start, end))

        # plot this data on a map
        max_map = selected_data.max(dim="time")
        qm = max_map.plot()
        ax = qm.axes
        ax.set_title(f"Maximum temperature values between {start} and {end}")
        ax.figure.savefig(save_as, bbox_inches="tight")
        plt.close(ax.figure)

        return float(selected_data.max())

    def min_tot(self, save_as="min_tot.png"):
        # Identify the minimum temperature over the whole dataset and plot

        # plot this data on a map
        min_map = self.tg.min(dim="time")
        qm = min_map.plot()
        ax = qm.axes
        ax.set_title("Overall minimum temperature values")
        ax.figure.savefig(save_as, bbox_inches="tight")
        plt.close(ax.figure)

        return float(self.tg.min())

    def max_tot(self, save_as="max_tot.png"):
        # Identify the maximum temperature over the whole dataset and plot

        # plot this data on a map
        max_map = self.tg.max(dim="time")
        qm = max_map.plot()
        ax = qm.axes
        ax.set_title("Overall maximum temperature values")
        ax.figure.savefig(save_as, bbox_inches="tight")
        plt.close(ax.figure)

        return float(self.tg.max())

    def monthly_max(self):
        return self.tg.resample(time="1M").max()

    def monthly_min(self):
        return self.tg.resample(time="1M").min()

    def yearly_max(self):
        return self.tg.resample(time="1YE").max()

    def yearly_min(self):
        return self.tg.resample(time="1YE").min()


# run from root of package
temp = TempExtremes("Data/Example_Data/e-obs_UK_ground_temp.nc")

"""print(temp.min_between('1950-01-01', '1955-01-01'))
print(temp.max_between('1950-01-01', '1955-01-01'))
print(temp.min_tot())
print(temp.max_tot())
print(type(temp.calc_monthly_max()))"""
