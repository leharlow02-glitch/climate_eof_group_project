import xarray as xr
import matplotlib.pyplot as plt
import os


class TempMean:

    def __init__(self, filepath, varname='tg'):

        # check the file exists
        if not os.path.exists(filepath):
            FileNotFoundError(f"File not found: {filepath}")

        # try to open the dataset
        try:
            self.ds = xr.open_dataset(filepath, decode_times=True)
            print('\nThe data exists, go on with analysis :)')
            print(f"Opened: {filepath}")
            print("Dimensions:", self.ds.dims)
            print("Variables:", list(self.ds.data_vars))

        # store the temperature variable
            self.tg = self.ds[varname]

        except Exception as e:
            raise RuntimeError(f"Error reading {filepath}: {e}")

    def mean_between(self, start, end, save_as='mean.png'):
        # Identify the mean temperature values between two dates and plot

        # select data between two dates
        selected_data = self.tg.sel(time=slice(start, end))

        # plot this data on a map
        mean_map = selected_data.mean(dim='time')
        qm = mean_map.plot()          # xarray returns an Axes object
        ax = qm.axes
        ax.set_title(f"Mean temperature values between {start} and {end}")
        ax.figure.savefig(save_as, bbox_inches='tight')
        plt.close(ax.figure)

        return float(selected_data.mean())
    
    def mean_tot(self, save_as='mean_tot.png'):
        # Identify the mean temperature over the whole dataset and plot

        # plot this data on a map
        mean_map = self.tg.mean(dim='time')
        qm = mean_map.plot()
        ax = qm.axes
        ax.set_title("Overall mean temperature values")
        ax.figure.savefig(save_as, bbox_inches='tight')
        plt.close(ax.figure)

        return float(self.tg.mean())

    def monthly_mean(self, month):
        return self.tg.resample(time="1M").mean()

    def yearly_mean(self):
        return self.tg.resample(time="1YE").mean()
    
    def monthly_clim(self):
        return self.tg.groupby('time.month').mean(dim='time')


tm = TempMean('Data/Example_Data/e-obs_UK_ground_temp.nc')
'''print(tm.mean_between('1950-01-01', '1955-01-01'))'''
print(tm.monthly_mean)