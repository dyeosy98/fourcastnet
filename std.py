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

    path = "/mnt/efs/processed/train"

    files = os.listdir(path)
    # print("files: ", files)

    means = []
    stds = []

    for i in range(0, len(h5params)):

        print(f'---\nAssessing {h5params[i]}...')

        for j in range(0, len(files)):
            
            with h5py.File(f'{path}/{files[j]}', 'r') as f:

                print(f'Assessing {files[j]}...')

                keys = list(f.keys())
                data_key = keys[0]
                param_key = keys[1]

                if j == 0:
                    data = f[data_key][:, i, :, :]
                else:
                    data = np.concatenate((data, f[data_key][:, i, : :]))

        #f[hour][param][latitude][longitude]
        #for every param, find mean of numbers for all hour, latitude, longitude

        print(f'Aggregating stds for {h5params[i]}...')
        stds.append(np.std(data))

    stds = np.array(stds)
    print(f'stds ({np.shape(stds)}): {stds}')
    np.save(
        "/home/ubuntu/fourcastnet/test_global_stds.npy", stds.reshape(1, -1, 1, 1)
    )

if __name__ == "__main__":
    main()
