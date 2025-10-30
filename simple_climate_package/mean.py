import xarray as xr
import matplotlib.pyplot as plt
import os
import pandas as pd
from simple_climate_package.loader import DataReader

class CalcMean:
    def __init__(self, file_path, varname='tg'):
        
        dr = DataReader(file_path)
        ds = dr.read()

        if varname not in ds:
            raise KeyError(f'{varname} not in dataset')
        self.tg = ds[varname]

        # check the file exists
        # if not os.path.exists(filepath):
        #     FileNotFoundError(f"File not found: {filepath}")

        # try to open the dataset
        # try:
        #     self.ds = xr.open_dataset(filepath, decode_times=True)
        #     print('\nThe data exists, go on with analysis :)')
        #     print(f"Opened: {filepath}")
        #     print("Dimensions:", self.ds.dims)
        #     print("Variables:", list(self.ds.data_vars))

        # # store the temperature variable
        #     self.tg = self.ds[varname]
        #     # print(self.tg.time)

        # except Exception as e:
        #     raise RuntimeError(f"Error reading {filepath}: {e}")
        

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
            # print(self.tg.time)

        except Exception as e:
            raise RuntimeError(f"Error reading {filepath}: {e}")
        
        # return self

    def mean_between(self, start, end):
        # Identify and returns the mean temperature values between two dates and plots it to a map.

        # select data between two dates
        selected_data = self.tg.sel(time=slice(start, end))

        # plot this data on a map
        mean_map = selected_data.mean(dim='time')

        return mean_map

    def plot_mean_between(self, start, end, save_path='/root/climate_eof_group_project/plots'):
        # Identify and returns the mean temperature values between two dates and plots it to a map.

        # create the diectory for the plots:
        os.makedirs(save_path, exist_ok=True)

        # select data between two dates
        selected_data = self.tg.sel(time=slice(start, end))

        # plot this data on a map
        mean_map = selected_data.mean(dim='time')
        qm = mean_map.plot(cmap='RdYlBu_r')          # xarray returns an Axes object
        ax = qm.axes
        ax.set_title(f"Mean {self.tg.name} values between {start} and {end}")
        ax.figure.savefig(save_path + f'/Mean_{self.tg.name}_values_between_{start}_and_{end}.png', bbox_inches='tight')
        plt.close(ax.figure)

        return mean_map

    def mean_tot_time(self):
        # Identify the mean temperature over the whole dataset

        return self.tg.mean(dim='time')
        
    def plot_mean_tot_time(self, save_path='/root/climate_eof_group_project/plots/'):
        # Identify the mean temperature over the whole dataset and plot

        # create the diectory for the plots:
        os.makedirs(save_path, exist_ok=True)

        # plot this data on a map
        mean_map = self.tg.mean(dim='time')
        qm = mean_map.plot(cmap='RdYlBu_r')
        ax = qm.axes
        ax.set_title(f"Overall mean {self.tg.name} values")
        ax.figure.savefig(save_path + f'mean_time_tot_{self.tg.name}.png', bbox_inches='tight')
        plt.close(ax.figure)

        return mean_map

    def monthly_mean(self):
        return self.tg.resample(time="1ME").mean()

    def yearly_mean(self):
        return self.tg.resample(time="1YE").mean()
    
    def plot_yearly_mean(self,out_dir="/root/climate_eof_group_project/plots/yearly_mean/"):
        
        # calculate the yearly mean:
        yearly_ds = self.yearly_mean()
        # da = yearly_ds[var]
        da = yearly_ds
        lats = yearly_ds.coords['latitude'].values
        lons = yearly_ds.coords['longitude'].values

        # 3. Compute global vmin/vmax for consistent color scaling
        vmin = float(da.min(skipna=True).values)
        vmax = float(da.max(skipna=True).values)

        # create the diectory for the plots:
        os.makedirs(out_dir, exist_ok=True)

        # cmap = "RdYlBu_r",

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
            plt.title(f"Mean {var_name} for {year_label}")
            plt.savefig(out_dir + f'mean {var_name} for {year_label}', dpi=150, bbox_inches="tight")
            fig.tight_layout()
            plt.close()
            print(f'sved fig for {year_label}')

    def monthly_clim(self):
        return self.tg.groupby('time.month').mean(dim='time')
    
    def monthly_clim_Anom(self):
        """
        Compute monthly anomalies:
        monthly mean - long-term monthly climatology.
        Returns an xarray.DataArray with one value per month.
        """
        # 1. Convert daily data → monthly means
        monthly = self.tg.resample(time="1ME").mean()

        # 2. Compute long-term monthly climatology
        clim = monthly.groupby("time.month").mean(dim="time")

        # 3. Subtract climatology from each month
        anom = monthly.groupby("time.month") - clim

        anom.attrs["description"] = "Monthly mean anomalies"
        return anom

    # DAILY climatology & anomalies (day-of-year handling)
    def daily_clim(self, drop_feb29=True):
        """
        Daily climatology (dayofyear: 1..365).
        If drop_feb29=True, Feb 29 is removed before computing the climatology so clim has 365 values.
        """
        daily = self.tg  # assume daily frequency; resample if needed: self.tg.resample(time="1D").mean()
        if drop_feb29:
            daily_no29 = daily.sel(time=~((daily['time'].dt.month == 2) & (daily['time'].dt.day == 29)))
        else:
            daily_no29 = daily
        clim = daily_no29.groupby("time.dayofyear").mean(dim="time")
        clim.attrs["description"] = "Daily climatology by dayofyear (1..365)"
        return clim


    def daily_clim_Anom(self, keep_feb29=True, drop_feb29_for_clim=True):
        """
        Daily anomalies: daily mean - day-of-year climatology.
        - If drop_feb29_for_clim=True, the climatology is computed on a 365-day calendar.
        - If keep_feb29=True, Feb 29 anomalies are produced by mapping Feb29 to Feb28 climatology.
        Otherwise Feb29 is dropped from the returned anomaly.
        Returns DataArray with same time axis as input (except possibly Feb29 if keep_feb29=False).
        """
        daily = self.tg  # use as-is (resample to 1D only if needed)

        # Optionally drop Feb29 when computing climatology
        if drop_feb29_for_clim:
            daily_for_clim = daily.sel(time=~((daily['time'].dt.month == 2) & (daily['time'].dt.day == 29)))
        else:
            daily_for_clim = daily

        clim = daily_for_clim.groupby("time.dayofyear").mean(dim="time")  # dayofyear: 1..365 (or 366)

        # Compute anomalies for days present in daily_for_clim
        # If we dropped Feb29 for climatology, we compute anom for non-Feb29 days first
        anom_non29 = daily_for_clim.groupby("time.dayofyear") - clim

        if keep_feb29 and drop_feb29_for_clim:
            # Build Feb29 anomalies by mapping to Feb28 climatology (common choice)
            feb29_mask = (daily['time'].dt.month == 2) & (daily['time'].dt.day == 29)
            if feb29_mask.any():
                # dayofyear for Feb28 in non-leap-year calendar:
                feb28_dayofyear = pd.Timestamp(year=2001, month=2, day=28).dayofyear  # usually 59
                feb28_clim = clim.sel(dayofyear=feb28_dayofyear)

                # Compute anomaly for Feb29 dates by subtracting Feb28 climatology
                feb29_values = daily.sel(time=feb29_mask) - feb28_clim

                # Combine non-Feb29 anomalies with constructed Feb29 anomalies and sort by time
                anom = xr.concat([anom_non29, feb29_values], dim="time").sortby("time")
            else:
                anom = anom_non29
        else:
            # either we dropped Feb29 and don't want to keep it, or climatology included Feb29 so the grouping works
            # if daily still has Feb29 but clim has 366 days, xarray alignment will work automatically.
            if not drop_feb29_for_clim:
                # We didn't drop Feb29 when computing climatology, so compute anom for full daily directly:
                anom = daily.groupby("time.dayofyear") - clim
            else:
                anom = anom_non29

        anom.attrs["description"] = "Daily anomalies (daily - dayofyear climatology)"
        return anom


    def plot_monthly_climatology(self,out_dir="/root/climate_eof_group_project/plots/monthly_clim/"):
        
        # calculate the yearly mean:
        clim_ds = self.monthly_clim()
        # da = yearly_ds[var]
        da = clim_ds
        lats = clim_ds.coords['latitude'].values
        lons = clim_ds.coords['longitude'].values

        # 3. Compute global vmin/vmax for consistent color scaling
        vmin = float(da.min(skipna=True).values)
        vmax = float(da.max(skipna=True).values)

        # create the diectory for the plots:
        os.makedirs(out_dir, exist_ok=True)

        # cmap = "RdYlBu_r",

        # print(da) 

        # loop to plot over the yearly data:
        times = da.month.values
        print(times)
        var_name = self.tg.name
        # print(self.tg.name)

        for idx, t in enumerate(times):
            single = da.isel(month=idx)

            # nice date label (YYYY)
            month_label = str(t)

            fig = plt.figure()
            ax = plt.axes()
            # single.plot()
            mesh = ax.pcolormesh(lons, lats, single.values, shading="auto", vmin=vmin, vmax=vmax, cmap="RdYlBu_r")
            cbar = fig.colorbar(mesh, ax=ax, orientation="vertical")
            cbar.set_label(var_name)
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            plt.title(f"Mean {var_name} for {month_label}")
            plt.savefig(out_dir + f'mean {var_name} for {month_label}', dpi=150, bbox_inches="tight")
            fig.tight_layout()
            plt.close()
            print(f'sved fig for {month_label}')

# print('Example data for the UK can be found here on the github repository: /root/climate_eof_group_project/Data/Example_Data/e-obs_UK_ground_temp.nc' )
# data_path = input('Input the path to the data you want to analyse: ')

# tm = TempMean(data_path)
# '''print(tm.mean_between('1950-01-01', '1955-01-01'))'''
# tm.plot_mean_tot_time()
# tm.plot_monthly_climatology()
# tm.plot_mean_between('1950-01-01', '1955-01-01')
# tm.plot_yearly_mean()
# month_clim = tm.monthly_clim()
# print(month_clim.shape)
# clim_amon = tm.monthly_clim_Anom()
# print(clim_amon.shape)
# day_clim = tm.daily_clim()
# print(day_clim.shape)
# daily_amon = tm.daily_clim_Anom()
# print(daily_amon.shape)

