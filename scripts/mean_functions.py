import os

import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr


def check_nc_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    try:
        ds = xr.open_dataset(file_path)
        print("\nThe data exists, go on with analysis :)")
        print(f"Opened: {file_path}")
        print("Dimensions:", ds.dims)
        print("Variables:", list(ds.data_vars))
        ds.close()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")


# read data for analysis:
def read_data(data_path):
    ds = xr.open_dataset(data_path)
    print("\nOverview:")
    print(ds)
    print("\nVariables:")
    print(ds.variables)  # List of variables
    print("\nCoordinates:")
    print(ds.coords)  # Coordinate variables
    return ds


def plot_time_mean(
    ds,
    var="tg",
    out_path="/root/climate_eof_group_project/plots/time_mean.png",
):
    """Compute mean of `var` over time and save plot to `out_path`."""
    temp_mean = calculate_time_mean(ds)
    plt.figure()
    temp_mean.plot()
    start_date = str(ds.time.min().values)[:10]
    end_date = str(ds.time.max().values)[:10]
    # Use variable’s long_name if available
    # var_long_name = getattr(ds[var], "long_name", var)
    var_name = getattr(ds[var], "name", var)
    # plt.title(f"Mean {var_long_name} from {start_date} to {end_date}")
    plt.title(f"Mean {var_name} from {start_date} to {end_date}")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()  # good practice in scripts
    print(f"Plot saved to: {out_path}")


def calculate_time_mean(ds):
    return ds["tg"].mean(dim="time")


def calculate_monthly_mean(ds):
    return ds.resample(time="1M").mean()


def calculate_yearly_mean(ds):
    return ds.resample(time="1YE").mean()


def plotting_yearly_mean(
    ds, var="tg", out_dir="/root/climate_eof_group_project/plots/yearly_mean/"
):

    # calculate the yearly mean:
    yearly_ds = calculate_yearly_mean(ds)
    da = yearly_ds[var]

    lats = yearly_ds.coords["latitude"].values
    lons = yearly_ds.coords["longitude"].values

    # 3. Compute global vmin/vmax for consistent color scaling
    vmin = float(da.min(skipna=True).values)
    vmax = float(da.max(skipna=True).values)

    # create the diectory for the plots:
    os.makedirs(out_dir, exist_ok=True)

    # cmap = "RdYlBu_r",

    # loop to plot over the yearly data:
    times = da.time.values
    print(times)
    var_name = getattr(ds[var], "name", var)

    for idx, t in enumerate(times):
        single = da.isel(time=idx)

        # nice date label (YYYY)
        year_label = pd.to_datetime(t).strftime("%Y")

        fig = plt.figure()
        ax = plt.axes()
        # single.plot()
        mesh = ax.pcolormesh(
            lons,
            lats,
            single.values,
            shading="auto",
            vmin=vmin,
            vmax=vmax,
            cmap="RdYlBu_r",
        )
        cbar = fig.colorbar(mesh, ax=ax, orientation="vertical")
        cbar.set_label(var)
        plt.title(f"Mean {var_name} for {year_label}")
        plt.savefig(
            out_dir + f"mean {var} for {year_label}",
            dpi=150,
            bbox_inches="tight",
        )
        fig.tight_layout()
        plt.close()
        print(f"sved fig for {year_label}")


print(
    "Example data for the UK can be found here on the github repository: "
    "/root/climate_eof_group_project/Data/Example_Data/e-obs_UK_ground_temp.nc"
)
data_path = input("Input the path to the data you want to analyse: ")

check_nc_file(data_path)
ds = read_data(data_path)
plot_time_mean(ds)
monthly_mean = calculate_monthly_mean(ds)
# print(monthly_mean)
print("\nshape of monthly mean:")
print(monthly_mean.tg.shape)
yearly_mean = calculate_yearly_mean(ds)
# print(monthly_mean)
print("\nshape of yearly mean:")
print(yearly_mean.tg.shape)

plotting_yearly_mean(ds)

# print(ds.tg.long_name)
