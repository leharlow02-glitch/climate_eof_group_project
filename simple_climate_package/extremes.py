import xarray as xr
import matplotlib.pyplot as plt
import os
import pandas as pd
from simple_climate_package.loader import DataReader

class CalcExtremes:
    def __init__(self, file_path, varname='tg'):
        dr = DataReader(file_path)
        ds = dr.read()

        if varname is None:
            varname = list(self.ds.data_vars)[0]

        if varname not in ds:
            raise KeyError(f'{varname} not in dataset')
        
        self.tg = ds[varname]

        # check the file exists
        # if not os.path.exists(filepath):
        #     FileNotFoundError(f"File not found: {filepath}")

        # # try to open the dataset
        # try:
        #     self.ds = xr.open_dataset(filepath, decode_times=True)
        #     print('\nThe data exists, go on with analysis :)')
        #     print(f"Opened: {filepath}")
        #     print("Dimensions:", self.ds.dims)
        #     print("Variables:", list(self.ds.data_vars))

        # # store the temperature variable
        #     self.tg = self.ds[varname]

        # except Exception as e:
        #     raise RuntimeError(f"Error reading {filepath}: {e}")

    def min_between(self, start, end):
        # Identify the minimum temperature values between two dates and plot

        # select data between two dates
        selected_data = self.tg.sel(time=slice(start, end))

        # plot this data on a map
        min_map = selected_data.min(dim='time')
        
        return min_map

    def plot_min_between(self, start, end, save_path='/root/climate_eof_group_project/plots'):
        # Identify the minimum temperature values between two dates and plot

        # select data between two dates
        selected_data = self.tg.sel(time=slice(start, end))

        # plot this data on a map
        min_map = selected_data.min(dim='time')
        qm = min_map.plot(cmap='RdYlBu_r')          # xarray returns an Axes object
        ax = qm.axes
        ax.set_title(f"Minimum {self.tg.name} values between {start} and {end}")
        ax.figure.savefig(save_path + f'/Min_{self.tg.name}_values_between_{start}_and_{end}.png', bbox_inches='tight')
        plt.close(ax.figure)

        return min_map

    def max_between(self, start, end):
        # Identify the maximum temperature values between two dates and plot

        # select data between two dates
        selected_data = self.tg.sel(time=slice(start, end))

        # plot this data on a map
        max_map = selected_data.max(dim='time')

        return max_map
    
    def plot_max_between(self, start, end, save_path='/root/climate_eof_group_project/plots'):
        # Identify the maximum temperature values between two dates and plot

        # select data between two dates
        selected_data = self.tg.sel(time=slice(start, end))

        # plot this data on a map
        max_map = selected_data.max(dim='time')
        qm = max_map.plot(cmap='RdYlBu_r')
        ax = qm.axes
        ax.set_title(f"Maximum {self.tg.name} values between {start} and {end}")
        ax.figure.savefig(save_path + f'/Max_{self.tg.name}_values_between_{start}_and_{end}.png', bbox_inches='tight')
        plt.close(ax.figure)

        return max_map


    def min_tot(self):
        # Identify the minimum temperature over the whole dataset and plot

        # plot this data on a map
        min_map = self.tg.min(dim='time')
        
        return min_map

    def plot_min_tot(self, save_path='/root/climate_eof_group_project/plots'):
        # Identify the minimum temperature over the whole dataset and plot

        # plot this data on a map
        min_map = self.tg.min(dim='time')
        qm = min_map.plot(cmap='RdYlBu_r')
        ax = qm.axes
        ax.set_title(f"Overall minimum {self.tg.name} values")
        ax.figure.savefig(save_path + f'/Min_{self.tg.name}_tot_time.png', bbox_inches='tight')
        plt.close(ax.figure)

        return min_map


    def max_tot(self):
        # Identify the maximum temperature over the whole dataset and plot

        # plot this data on a map
        max_map = self.tg.max(dim='time')
        
        return max_map

    def plot_max_tot(self, save_path='/root/climate_eof_group_project/plots'):
        # Identify the maximum temperature over the whole dataset and plot

        # plot this data on a map
        max_map = self.tg.max(dim='time')
        qm = max_map.plot(cmap='RdYlBu_r')
        ax = qm.axes
        ax.set_title(f"Overall maximum {self.tg.name} values")
        ax.figure.savefig(save_path + f'/Max_{self.tg.name}_tot_time.png', bbox_inches='tight')
        plt.close(ax.figure)

        return max_map

    def monthly_max(self):
        return self.tg.resample(time="1ME").max()

    def plot_yearly_max(self,out_dir="/root/climate_eof_group_project/plots/yearly_max/"):
        
        # calculate the yearly mean:
        yearly_ds = self.yearly_max()
        # da = yearly_ds[var]
        da = yearly_ds
        lats = yearly_ds.coords['latitude'].values
        lons = yearly_ds.coords['longitude'].values

        # 3. Compute global vmin/vmax for consistent color scaling
        vmin = float(da.min(skipna=True).values)
        vmax = float(da.max(skipna=True).values)

        # create the diectory for the plots:
        os.makedirs(out_dir, exist_ok=True)

        # loop to plot over the yearly data:
        times = da.time.values
        print(times)
        var_name = self.tg.name

        for idx, t in enumerate(times):
            single = da.isel(time=idx)

            # nice date label (YYYY)
            year_label = pd.to_datetime(t).strftime("%Y")

            fig = plt.figure()
            ax = plt.axes()
            # single.plot()
            mesh = ax.pcolormesh(lons, lats, single.values, shading="auto", vmin=vmin, vmax=vmax, cmap="RdYlBu_r")
            cbar = fig.colorbar(mesh, ax=ax, orientation="vertical")
            cbar.set_label(var_name)
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            plt.title(f"Max {var_name} for {year_label}")
            plt.savefig(out_dir + f'max {var_name} for {year_label}', dpi=150, bbox_inches="tight")
            fig.tight_layout()
            plt.close()
            print(f'sved fig for {year_label}')

    def plot_yearly_min(self,out_dir="/root/climate_eof_group_project/plots/yearly_min/"):
        
        # calculate the yearly mean:
        yearly_ds = self.yearly_min()
        # da = yearly_ds[var]
        da = yearly_ds
        lats = yearly_ds.coords['latitude'].values
        lons = yearly_ds.coords['longitude'].values

        # 3. Compute global vmin/vmax for consistent color scaling
        vmin = float(da.min(skipna=True).values)
        vmax = float(da.max(skipna=True).values)

        # create the diectory for the plots:
        os.makedirs(out_dir, exist_ok=True)

        # loop to plot over the yearly data:
        times = da.time.values
        print(times)
        var_name = self.tg.name

        for idx, t in enumerate(times):
            single = da.isel(time=idx)

            # nice date label (YYYY)
            year_label = pd.to_datetime(t).strftime("%Y")

            fig = plt.figure()
            ax = plt.axes()
            # single.plot()
            mesh = ax.pcolormesh(lons, lats, single.values, shading="auto", vmin=vmin, vmax=vmax, cmap="RdYlBu_r")
            cbar = fig.colorbar(mesh, ax=ax, orientation="vertical")
            cbar.set_label(var_name)
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            plt.title(f"Min {var_name} for {year_label}")
            plt.savefig(out_dir + f'min {var_name} for {year_label}', dpi=150, bbox_inches="tight")
            fig.tight_layout()
            plt.close()
            print(f'sved fig for {year_label}')

    def monthly_min(self):
        return self.tg.resample(time="1ME").min()

    def yearly_max(self):
        return self.tg.resample(time="1YE").max()

    def yearly_min(self):
        return self.tg.resample(time="1YE").min()

# run from root of package
# temp = TempExtremes('Data/Example_Data/e-obs_UK_ground_temp.nc')

'''print(temp.min_between('1950-01-01', '1955-01-01'))
print(temp.max_between('1950-01-01', '1955-01-01'))
print(temp.min_tot())
print(temp.max_tot())
print(type(temp.calc_monthly_max()))'''
