from botocore.config import Config
import h5py
import os
import numpy as np
import yaml

def generate_params_list(config):

    pl_params = config["pl_params"]
    sfc_params = config["sfc_params"]
    pressure_levels = config["pressure_levels"]

    params = []

    for param in pl_params:
        for pressure_level in pressure_levels[param]:
            params.append(f'{param}{pressure_level}')
    for param in sfc_params:
        params.append(param)

    return params

def main():

    # Initialize config
    print("Initializing config...")
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    h5params = generate_params_list(config)
    print("h5params: ", h5params)

    # path = "/efs/processed/test"
    path = "/home/ubuntu/test_data"

    files = os.listdir(path)
    print("files: ", files)

    for file in files:
        f = h5py.File(f'{path}/{file}', 'r')
        keys = list(f.keys())
        print("keys: ", keys)
        data_key = keys[0]
        print("data_key: ", data_key)
        param_key = keys[1]
        print("param_key: ", param_key)

        print(np.shape(f[data_key]))
        print(f[param_key][0])

        print("mean: ", np.mean(f[data_key], (0,2,3)))

    #f[hour][param][latitude][longitude]
    #for every param, find mean of numbers for all hour, latitude, longitude

    for h5param in h5params:
        print(f[h5param])
        # print("mean: ", np.mean())
        

# Open the zarr files and construct the xarray from them
    # zarr_arrays = [xr.open_zarr(path) for path in zarr_paths]
    # era5_xarray = xr.concat(
    #     [z[list(z.data_vars.keys())[0]] for z in zarr_arrays], dim="channel"
    # )
    # era5_xarray = era5_xarray.transpose("time", "channel", "latitude", "longitude")
    # era5_xarray.name = "fields"
    # era5_xarray = era5_xarray.astype("float32")

    # # Save mean and std
    # stats_path = os.path.join(cfg.hdf5_store_path, "stats")
    # print(f"Saving global mean and std at {stats_path}")
    # if not os.path.exists(stats_path):
    #     os.makedirs(stats_path)
    # era5_mean = np.array(
    #     era5_xarray.mean(dim=("time", "latitude", "longitude")).values
    # )
    # np.save(
    #     os.path.join(stats_path, "global_means.npy"), era5_mean.reshape(1, -1, 1, 1)
    # )
    # era5_std = np.array(
    #     era5_xarray.std(dim=("time", "latitude", "longitude")).values
    # )
    # np.save(
    #     os.path.join(stats_path, "global_stds.npy"), era5_std.reshape(1, -1, 1, 1)
    # )
    # print(f"Finished saving global mean and std at {stats_path}")



if __name__ == "__main__":
    main()
