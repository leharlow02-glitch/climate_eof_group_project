from functools import wraps
import os
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from scipy.stats import t

###Writing linear regression calculation and plotting class###

class linear_regression:
    """
    Load dataset, compute anomalies (optional), calculate
    linear regression for each point across lon-lat grid, and plot
    slope change per decade over a spatial map
    """

    # reading in data function
    def __init__(self, data_dir_path, varname=None):
        self.ds = xr.open_dataset(data_dir_path)
        if varname is None:
            varname = list(self.ds.data_vars)[0]
        # Takes the first variable in the 3D array
        self.varname = varname
        self.da = self.ds[self.varname]

        # variables names and creating empty fields for computing
        self.lat = "lat" if "lat" in self.da.coords else "latitude"
        self.lon = "lon" if "lon" in self.da.coords else "longitude"
        self.results = {}

    # resampling daily data to years
    def make_yearly(self, how="mean"):
        self.annual = self.da.resample(time="1YS").reduce(getattr(np, how))
        return self.annual

    def ignore_numpy_warnings(func):
        """
        Runs function inside np.errstat(invalid='ignore', divide='ignore)
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            with np.errstate(invalid="ignore", divide="ignore"):
                return func(*args, **kwargs)

        return wrapper

    @ignore_numpy_warnings
    def grid_linear_regression(self, min_obs=3):
        """
        Function computes a linear regression for each grid point in
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

        if self.annual is None:
            self.make_yearly()

        da = self.annual.transpose("time", self.lat, self.lon)
        y = da.values[:, :, :]  # 3D array with time, lat, lon

        years = da["time"].dt.year.values.astype(float)

        # Validate data array shapes:
        if y.ndim != 3:
            raise ValueError("y must be 3D with shape (time ny, nx)")
        T, ny, nx = y.shape
        if len(years) != T:
            raise ValueError(
                "Length of x must equal y shape[0] (time dimension)"
            )

        # Create lon-lat grid
        N_grid = ny * nx

        # Reshape 3D y to 2D array (T, N_grid)
        Y = y.reshape(T, N_grid)

        # Reshape X so broadcasting occurs across the array correctly
        X = years.reshape(T, 1)
        X_mat = np.broadcast_to(X, (T, N_grid))

        # Validate obs using mask and counts to mask NaNs
        valid = ~np.isnan(Y)
        n_obs = valid.sum(axis=0).astype(float)

        # Fill invalid regions with zero for sums
        Yf = np.where(valid, Y, 0.0)

        # Calculate sums
        X_sum = (X_mat * valid).sum(axis=0)
        Y_sum = Yf.sum(axis=0)

        # Calculate means
        X_mean = np.where(n_obs > 0, X_sum / n_obs, np.nan)
        Y_mean = np.where(n_obs > 0, Y_sum / n_obs, np.nan)

        # Center data array shapes
        Xc = (X_mat - X_mean.reshape(1, N_grid)) * valid
        Yc = (Yf - Y_mean.reshape(1, N_grid)) * valid

        # Sxx and Sxy
        Sxx = np.sum(Xc * Xc, axis=0)
        Sxy = np.sum(Xc * Yc, axis=0)

        # Minimum data maks so variables are only c
        # computed where valid results are present
        ok_pix = (n_obs >= min_obs) & (Sxx != 0)

        # Create empty output files
        slope, intercept, t_stat, p_value, r2, rmse = [
            np.full(N_grid, np.nan, dtype=float) for i in range(6)
        ]

        # Compute slope and intercept
        slope_ok = Sxy[ok_pix] / Sxx[ok_pix]
        slope[ok_pix] = slope_ok
        intercept[ok_pix] = Y_mean[ok_pix] - slope_ok * X_mean[ok_pix]

        # Compute slope per decade and over whole dataset
        total_change = slope * (years[-1] - years[0])
        per_decade = slope * 10.0

        # Comparing model_predicted values and residuals
        # Measures how well the linear regression fits each lon-lat
        # grid point
        Yhat = np.zeros_like(Yf)
        if np.any(ok_pix):
            idx_ok = np.where(ok_pix)[0]  # compute for ok grid points
            # broadcast to 2D array shape
            Yhat[:, idx_ok] = (slope[idx_ok].reshape(1, -1) * X) + intercept[
                idx_ok
            ].reshape(1, -1)
            Yhat = np.where(valid, Yhat, 0.0)  # mask out invalid times
        # Calculating residuals
        resid = Yf - Yhat
        SSR = np.sum(resid * resid, axis=0)  # Sum of squared residuals

        # Calculating mean squared error
        df = n_obs - 2.0  # Degrees of freedom
        mse = SSR / df
        se_slope = np.sqrt(mse / Sxx)

        # Calcuating t-statistics and p-values
        t_stat = slope / se_slope
        p_value = 2.0 * t.sf(np.abs(t_stat), df)

        # Calculating R squared and RMSE
        SST = np.sum(((Yf - Y_mean.reshape(1, N_grid)) * valid) ** 2, axis=0)
        r2 = 1.0 - SSR / SST
        rmse = np.sqrt(SSR / n_obs)

        lat_vals = da.coords[self.lat].values
        lon_vals = da.coords[self.lon].values

        # reshape to (ny,nx)
        def to_grid(a):
            return a.reshape(ny, nx)

        ds_out = xr.Dataset(
            {
                "slope": ((self.lat, self.lon), to_grid(slope)),
                "intercept": ((self.lat, self.lon), to_grid(intercept)),
                "t_stat": ((self.lat, self.lon), to_grid(t_stat)),
                "p_value": ((self.lat, self.lon), to_grid(p_value)),
                "r2": ((self.lat, self.lon), to_grid(r2)),
                "rmse": ((self.lat, self.lon), to_grid(rmse)),
                "n_obs": ((self.lat, self.lon), to_grid(n_obs)),
                "per_decade": ((self.lat, self.lon), to_grid(per_decade)),
                "total_change": ((self.lat, self.lon), to_grid(total_change)),
            },
            coords={self.lat: lat_vals, self.lon: lon_vals},
        )

        self.results = ds_out
        return self.results

    def quick_plot_signif_stippling(self, key="per_decade", out_dir="/root/climate_eof_group_project/plots/linear_regression/"):
        # read in data
        field = self.results[key]
        p_val = self.results["p_value"]

        # set up spatial lon-lat grid
        lons = self.da[self.lon].values
        lats = self.da[self.lat].values
        Lon, Lat = np.meshgrid(lons, lats)

        # create figure
        fig, ax = plt.subplots(figsize=(7, 6))

        # making significance mask
        p_95 = np.ma.masked_greater(p_val, 0.05)

        # constraints on colourbar for plotting
        vmin, vmax = np.nanmin(field), np.nanmax(field)

        # plotting
        plot = plt.contourf(
            Lon,
            Lat,
            field,
            levels=100,
            cmap=plt.get_cmap("hot_r"),
            vmin=vmin,
            vmax=vmax,
            extend="both",
        )
        plt.contourf(Lon, Lat, p_95, hatches=[".."], alpha=0.0)

        # creating colourbar
        cbar = fig.colorbar(
            plot, orientation="horizontal", shrink=0.7, pad=0.27
        )
        cbar.set_label("Change in slope per decade", rotation=0, fontsize=8)
        tick_min, tick_max = np.nanmin(field), np.nanmax(field)
        ticks = np.linspace(
            vmin, vmax, 6
        )  # creates 6 evenly spaced ticks
        cbar.set_ticks(ticks)
        cbar.ax.set_xticklabels(
            [f"{t:.2f}" for t in ticks]
        )  # formats to 2 decimal places

        # labelling axes
        ax.set_xlabel("Longitude", labelpad=15, fontsize=10)
        ax.set_ylabel("Latitude", labelpad=15, fontsize=10)

        #Save plot
        os.makedirs(out_dir, exist_ok=True)
        plt.title(f"Linear regression of {self.da}")
        plt.savefig(out_dir + f' linear regression of {self.da}', dpi=150, bbox_inches="tight")
        fig.tight_layout()

        #show and close plot
        plt.show()
        plt.close()
        print(f'sved fig')

