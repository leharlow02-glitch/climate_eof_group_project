from scipy import stats
import numpy as np
from scipy.stats import t
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
from cartopy import feature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mplticker
import matplotlib.colors as mcolors
### Writing a function to perform a linear regression on e-obs UK data
#time = UNLIMITED ; // (27210 currently)
#longitude = 44
#latitude = 36


def compute_anomalies(da, baseline=("1961-01-01", "1990-12-31"), method="monthly"):
    """
    Compute climate anomalies relative to a baseline period.

    Parameters
    ----------
    da : xarray.DataArray
        Input data with time dimension ('time', 'lat', 'lon').
    baseline : tuple of str
        Start and end date (e.g. ("1961-01-01", "1990-12-31")) defining baseline period.
    method : {"monthly", "annual", "simple"}
        Type of anomalies to compute:
        - "monthly": subtracts monthly climatology (removes seasonal cycle)
        - "annual": resamples to yearly means and removes baseline mean
        - "simple": subtracts mean of baseline period (no seasonal cycle removal)

    Returns
    -------
    anoms : xarray.DataArray
        Anomaly DataArray with same shape as input (for "monthly"/"simple")
        or annual shape (for "annual").
    """

    if "time" not in da.dims:
        raise ValueError("DataArray must have a 'time' dimension.")

    baseline_start, baseline_end = baseline
    baseline_da = da.sel(time=slice(baseline_start, baseline_end))

    if method == "monthly":
        # Compute monthly climatology over baseline
        clim = baseline_da.groupby("time.month").mean("time")
        # Subtract monthly mean from each corresponding month
        anoms = da.groupby("time.month") - clim
    elif method == "annual":
        # Aggregate to annual means
        annual = da.resample(time="1Y").mean("time")
        baseline_mean = annual.sel(time=slice(baseline_start, baseline_end)).mean("time")
        anoms = annual - baseline_mean
    elif method == "simple":
        baseline_mean = baseline_da.mean("time")
        anoms = da - baseline_mean
    else:
        raise ValueError("method must be one of {'monthly', 'annual', 'simple'}")

    # Add helpful attributes
    anoms.attrs = da.attrs.copy()
    anoms.attrs["long_name"] = f"{da.name or 'variable'} anomalies"
    anoms.attrs["description"] = f"Anomalies computed using {method} method relative to {baseline_start}–{baseline_end}"

    return anoms

def linear_regression_each_pixel(x, y, min_obs=3):
    """
    Linear regression across the time axis=0 for each pixel in lon,
    lat grid. 
    Inputs:
        data: 
        x= 1D array, shape [T]
        Independent variable - length must match y.shape[0]
        y= 3D array, [T, ny, nx]
            Dependent variable across time and lon-lat grid
    Returns:
        slopes, y-intercept, tstats, p-val, r2, rmse, n_obs
        at each pixel
    Additional notes:
        - Handles NaNs
        - Produces NaNs when n_obs <3
    """
    # validate
    if y.ndim != 3:
        raise ValueError("y must be 3D with shape (time, ny, nx)")
    T, ny, nx = y.shape
    if len(x) != T:
        raise ValueError("Length of x must equal y.shape[0] (time dimension)")

    N_grid = ny * nx

    # reshape 3D Y to a 2D array (T, N_grid))
    Y = y.reshape(T, N_grid)            
    # Make X_mat explicitly (T, N_grid) so broadcasting is unambiguous
    X = np.asarray(x).reshape(T, 1)     
    X_mat = np.broadcast_to(X, (T, N_grid))  

    # valid mask and counts
    valid = ~np.isnan(Y)                
    n_obs = valid.sum(axis=0).astype(float) 

    # fill invalid regions with zero for sums
    Yf = np.where(valid, Y, 0.0)

    # sums
    X_sum = (X_mat * valid).sum(axis=0)   
    Y_sum = Yf.sum(axis=0)              

    # means 
    with np.errstate(divide='ignore', invalid='ignore'):
        X_mean = np.where(n_obs > 0, X_sum / n_obs, np.nan)   
        Y_mean = np.where(n_obs > 0, Y_sum / n_obs, np.nan)

    # center- make X_mean shape (1, Npix) to broadcast across time
    Xc = (X_mat - X_mean.reshape(1, N_grid)) * valid   
    Yc = (Yf - Y_mean.reshape(1, N_grid)) * valid

    # Sxx and Sxy
    Sxx = np.sum(Xc * Xc, axis=0)   
    Sxy = np.sum(Xc * Yc, axis=0)

    # minimum-data mask and Sxx nonzero
    ok_pix = (n_obs >= min_obs) & (Sxx != 0)

    # prepare outputs
    slope = np.full(N_grid, np.nan, dtype=float)
    intercept = np.full(N_grid, np.nan, dtype=float)
    t_stat = np.full(N_grid, np.nan, dtype=float)
    p_value = np.full(N_grid, np.nan, dtype=float)
    r2 = np.full(N_grid, np.nan, dtype=float)
    rmse = np.full(N_grid, np.nan, dtype=float)

    # compute slope/intercept only where ok
    slope_ok = Sxy[ok_pix] / Sxx[ok_pix]
    slope[ok_pix] = slope_ok
    intercept[ok_pix] = Y_mean[ok_pix] - slope_ok * X_mean[ok_pix]

    #compute slope over whole dataset (1950-2024)
    total_change = slope * (x[-1] - x[0])  # °C over full period    
    per_decade = slope * 10.0              # °C per decade


    # predictions & residuals (only for ok pixels)
    # build predicted (T, Npix) but zero where invalid 
    Yhat = np.zeros_like(Yf)
    if np.any(ok_pix):
        # compute for ok pixels only
        idx_ok = np.where(ok_pix)[0]
        # broadcasting: slope[idx_ok] -> (1, n_ok)
        Yhat[:, idx_ok] = (slope[idx_ok].reshape(1, -1) * X) + intercept[idx_ok].reshape(1, -1)
        # mask out invalid times
        Yhat = np.where(valid, Yhat, 0.0)

    resid = Yf - Yhat
    SSR = np.sum(resid * resid, axis=0)   # (Npix,)

    # df and mse
    df = n_obs - 2.0
    with np.errstate(invalid='ignore', divide='ignore'):
        mse = SSR / df
        se_slope = np.sqrt(mse / Sxx)

    # t-stat and p-value 
    with np.errstate(invalid='ignore', divide='ignore'):
        tvals = slope / se_slope
        pvals = 2.0 * t.sf(np.abs(tvals), df)

    t_stat = tvals
    p_value = pvals

    # R2 and RMSE
    SST = np.sum(((Yf - Y_mean.reshape(1, N_grid)) * valid)**2, axis=0)
    with np.errstate(invalid='ignore', divide='ignore'):
        r2vals = 1.0 - SSR / SST
        rmse_vals = np.sqrt(SSR / n_obs)

    r2 = r2vals
    rmse = rmse_vals

    # reshape back to (ny, nx)
    def to_grid(arr):
        return arr.reshape(ny, nx)

    return {
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


def plot_slope_map_signif_stippling(per_decade, p_value, longitude, latitude):
    #set up map
    Lon, Lat = np.meshgrid(longitude, latitude)
    fig, ax = plt.subplots(figsize=(7,7))

    #Making significance mask
    p_uk = p_value [:,:]
    p_95= np.ma.masked_greater(p_uk, 0.05)

    #add color bar
    vmin, vmax = np.nanmin(per_decade), np.nanmax(per_decade)

    plot = plt.contourf(Lon, Lat, per_decade, levels = 100, cmap=plt.get_cmap('hot_r'), vmin= vmin, vmax=vmax, extend='both')
    plt.contourf(Lon, Lat, p_95, hatches = [".."],  alpha=0.0)


    cbar = fig.colorbar(plot, orientation='horizontal',  shrink=0.7, pad=0.27)
    cbar.set_label('Change in \u00B0C per decade', rotation=0, fontsize=8)
    #cbar.ax.tick_params(labelsize=7, length=0)
    # Compute evenly spaced ticks across your value range
    tick_min, tick_max = np.nanmin(per_decade), np.nanmax(per_decade)
    ticks = np.linspace(tick_min, tick_max, 6)  # 6 evenly spaced ticks
    cbar.set_ticks(ticks)
    cbar.ax.set_xticklabels([f"{t:.2f}" for t in ticks])  # format to 2 decimals

    ax.set_xlabel('Longitude', labelpad=15, fontsize=10)
    ax.set_ylabel('Latitude', labelpad=15, fontsize=10)

    fig.tight_layout()
    plt.show()


 
# 1. Open dataset
time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)

# pass the coder to decode_times
ds = xr.open_dataset("Data/Example_Data/e-obs_UK_ground_temp.nc",
                     decode_times=time_coder)

# 2. Pick your variable (e.g. temperature)
var_name = 'tg'  # change if needed (e.g., 'temperature', 'tas', etc.)
da = ds[var_name]  # this should have dims ('time', 'lat', 'lon')

# 3. Create fractional years for the regression x-axis
time = ds['time']
years = time.dt.year.values
doy = time.dt.dayofyear.values
is_leap = time.dt.is_leap_year.values
days_in_year = np.where(is_leap, 366, 365)
x = years + (doy - 1) / days_in_year  # 1D array of fractional years

# 4. Extract the data variable as a NumPy array
y = da.values  # shape (time, lat, lon)

# 5. Run your regression
out = linear_regression_each_pixel(x, y)

# 6. Plot slope map
plot_slope_map_signif_stippling(out['per_decade'], out['p_value'], ds['longitude'].values, ds['latitude'].values
               )


    
