from scipy import stats
import numpy as np
from scipy.stats import t
import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.colors as mcolors
from functools import wraps

###Writing linear regression calculation and plotting class###

class linear_regression():
    """ Load dataset, compute anomalies (optional), calculate 
    linear regression for each point across lon-lat grid, and plot 
    slope change per decade over a spatial map """

    #reading in data function
    def __init__(self, data_dir_path):
        self.ds = xr.open_dataset(data_dir_path)
        varname = list(self.ds.data_vars)[0]
        self.da = self.ds[self.varname]

        #variables names and creating empty fields for computing
        self.lat = 'lat' if 'lat' in self.da.coords else 'latitude'
        self.lon= 'lon' if 'lon' in self.da.coords else 'longitude'
        self.anoms = None 
        self.results = {}

    #computing monthly anoms by subtracting the climatological mean
    def compute_monthly_anoms(self, baseline=None):

        if baseline is None:
            base = self.da
        else:
            try:
                start,end = baseline
            except Exception:
                raise ValueError('Baseline must be a typle or None')
            base = self.da.sel(time=slice(start,end))
        clim = base.groupby('time.month').mean('time')
        self.anoms = self.da.groupby('time.month') - clim
        print(self.anoms)
        return self.anoms
    
    #computing fractional years
    """since array is daily, fractional years are needed 
    to perform an accurate linear regression"""

    def create_years(self):
        #creates a 1D array of fractional years
        time = self.da['time']
        years = time.dt.year.values
        doy = time.dt.dayofyear.values
        is_leap = time.dt.is_leap_year.values
        days_in_year= np.where(is_leap, 366, 365)
        self.x = years + (doy - 1)/ days_in_year
        print(self.x)
        if self.x != self.anoms:
            raise ValueError('Time dimensions do not match')
        return self.x
    
    def ignore_numpy_warmings(func):
        """ Runs function inside np.errstat(invalid='ignore', divide='ignore)"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with np.errstate(invalid='ignore', divide= 'ignore'):
                return func(*args, **kwargs)
        return wrapper
    
    @ignore_numpy_warmings
    def grid_linear_regression(self, use_anoms= True, min_obs=3):
        """ Function computes a linear regression for each grid point in
        dataset's longitude-latitude grid. 
        
        It returns the following information:
        - slope per year (slope)
        - slope per decade (per_decade)
        - total change (total_change)
        - p_value for significance (p_val)
        - number of observations (n_obs)
        - R squared (r2)
        - Root mean squared error (rmse)
        - intercept (intercept)
        """
        da = self.anoms if (use_anoms and self.anoms is not None) else self.da
        y = da.values[:,:,:] #3D array with time, lat, lon

        if self.x is None:
            self.build_years(use_anoms=use_anoms)
        x = self.x  # 1D array with fractional years
        
        #Validate data array shapes:
        if y.ndim != 3:
            raise ValueError('y must be 3D with shape (time ny, nx)')
        T, ny, nx = y.shape
        if len(x) != T:
            raise ValueError('Length of x must equal y shape[0] (time dimension)')
        
        #Create lon-lat grid
        N_grid = ny * nx

        #Reshape 3D y to 2D array (T, N_grid)
        Y = y.reshape(T, N_grid)
        
        #Reshape X so broadcasting occurs across the array correctly
        X = np.asarray(x).reshape(T,1)
        X_mat = np.broadcast_to(X, (T, N_grid))

        #Validate obs using mask and counts to mask NaNs
        valid = ~np.isnan(Y)
        n_obs = valid.sum(axis=0).astype(float)

        #Fill invalid regions with zero for sums 
        Yf = np.where(valid, Y, 0.0)

        #Calculate sums
        X_sum = (X_mat * valid).sum(axis=0)
        Y_sum = Yf.sum(axis=0)

        #Calculate means
        X_mean = np.where(n_obs > 0, X_sum/n_obs, np.nan)
        Y_mean = np.where(n_obs >0, Y_sum/ n_obs, np.nan)
        
        # Center data array shapes
        Xc = (X_mat- X_mean.reshape(1, N_grid)) * valid
        Yc = (Yf - Y_mean.reshape(1, N_grid)) * valid

        #Sxx and Sxy
        Sxx = np.sum(Xc * Xc, axis=0)
        Sxy = np.sum(Xc * Yc, axis=0)

        #Minimum data maks so variables are only computed where valid results are present
        ok_pix = (n_obs >= min_obs) and (Sxx != 0)

        #Create empty output files
        slope, intercept, t_stat, p_value, r2, rmse = [np.full(N_grid, np.nan, dtype=float) for i in range(6)]

        #Compute slope and intercept 
        slope_ok = Sxy[ok_pix]/ Sxx[ok_pix]
        slope[ok_pix] = slope_ok
        intercept[ok_pix] = Y_mean[ok_pix] - slope_ok * X_mean[ok_pix]

        #Compute slope per decade and over whole dataset
        total_change = slope * (x[-1] - x[0])
        per_decade = slope * 10.0

        #Comparing model_predicted values and residuals
        """ Measures how well the linear regression fits each lon-lat
        grid point """
        Yhat = np.zeros_like(Yf)
        if np.any(ok_pix):
            idx_ok = np.where(ok_pix)[0] #compute for ok grid points
            Yhat[:,idx_ok]= (slope[idx_ok].reshape(1,-1)* X) +intercept[idx_ok].reshape(1,-1) #broadcast to 2D array shape
            Yhat = np.where(valid, Yhat, 0.0) #mask out invalid times
        #Calculating residuals
        resid = Yf - Yhat
        SSR = np.sum(resid * resid, axis=0) #sum of squared residuals

        #Calculating mean squared error
        df = n_obs - 2.0 #degrees of freedom
        mse = SSR/df
        se_slope = np.sqrt(mse/Sxx)

        #Calcuating t-statistics and p-values
        t_stat = slope/ se_slope
        p_value = 2.0 * t.sf(np.abs(t_stat), df)

        #Calculating R squared and RMSE
        SST = np.sum(((Yf- Y_mean.reshape(1,N_grid)) * valid)** 2, axis=0)
        r2 = 1.0 - SSR/SST
        rmse = np.sqrt(SSR/n_obs)

        #reshape to (ny,nx)
        def to_grid(a):
            return a.reshape(ny, nx)
        
        self.results = {
            'slope': to_grid(slope),
            'intercept': to_grid(intercept),
            't_stat': to_grid(t_stat),
            'p_value': to_grid(p_value),
            'r2': to_grid(r2),
            'rmse': to_grid(rmse),
            'n_obs': to_grid(n_obs),
            'per_decade': to_grid(per_decade),
            'total_change': to_grid(total_change)
        }
        return self.results

    def quick_plot_signif_stippling(self, key='per_decade'):
        #read in data
        field = self.results[key]
        p_val = self.results['p_value']

        #set up spatial lon-lat grid
        lons = self.da[self.long].values
        lats = self.da[self.lat].values
        Lon, Lat = np.meshgrid(lons, lats)

        #create figure
        fig, ax = plt.subplots(figsize= (7,6))
        
        #making significance mask
        p_95 = np.ma.masked_greater(p_val, 0.05)

        #constraints on colourbar for plotting
        vmin, vmax = np.nanmin(field), np.nanmax(field)

        #plotting
        plot= plt.contourf(Lon, Lat, field, levels= 100,
        cmap= plt.get_cmap('hot_r'), vmin= vmin, vmax= vmax,
        extend= 'both')
        plt.contourf(Lon, Lat, p_95, hatches = [".."], alpha = 0.0)

        #creating colourbar
        cbar = fig.colorbar(plot, orientation= 'horizontal', shrink= 0.7, pad=0.27)
        cbar.set_label('Change in slope per decade', rotation = 0, fontsize= 8)
        tick_min, tick_max = np.nanmin(field), np.nanmax(field)
        ticks = np.linspace(tick_min, tick_max, 6) #creates 6 evenly spaced ticks
        cbar.set_ticks(ticks)
        cbar.ax.set_xticklabels([f"t:.2f" for t in ticks]) #formats to 2 decimal places

        #labelling axes
        ax.set_xlabel('Longitude', labelpad= 15, fontsize= 10)
        ax.set_ylabel('Latitude', labelpad=15, fontsize = 10)
        plt.show()









