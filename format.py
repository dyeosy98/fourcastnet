import boto3
import botocore
from botocore import UNSIGNED
from botocore.config import Config
from datetime import date, timedelta
import h5py
import os
import numpy as np
# import random
import yaml

def get_file_date(filename):

    date = filename.split("-")[-1]
    start_date, end_date = date[:-3].split('_')
    start_date = start_date[4:8]
    end_date = end_date[4:8]

    return start_date, end_date


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


def is_leap_year(year):
    
    if year % 4 == 0:
        return 1
    else:
        return 0


def get_days_in_month(month):

    days_in_month = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31, 
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30, 
    12: 31
    }

    days = days_in_month[month]

    return days


def get_hour_index(year, start_month, start_day, hour, dt):

    days_in_month = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31, 
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30, 
    12: 31
    }

    hour_index = 0

    for month in range(1, 13):

        if int(start_month) == int(month):
            hour_index += (start_day - 1) * 24 / dt
            break
        else:
            if month == 2:
                if is_leap_year(year):
                    hour_index += (get_days_in_month(month) + 1) * 24 / dt
                else:
                    hour_index += get_days_in_month(month) * 24 / dt
            else:
                hour_index += get_days_in_month(month) * 24 / dt
    
    hour_index += hour / dt

    return int(hour_index)


def main():

    # Initialize config
    print("Initializing config...")
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    data_path = config["download_path"]
    nc_files = os.listdir(data_path)
    #print(nc_files)

    write_path = config["write_path"]
    if os.path.exists(write_path):
        print(f'{write_path} exists, skipping directory creation...')
    else:
        print(f'{write_path} does not exist, creating directory...')
        os.mkdir(write_path)

    train_years = list(range(config["start_train_year"], config["end_train_year"] + 1))
    test_years = config["test_years"]
    out_of_sample_years = config["out_of_sample_years"]
    all_years = train_years + test_years + out_of_sample_years

    h5params = generate_params_list(config)

    # Create an H5 file for each year of data

    # for year in ["2014"]: # TODO: Update to all years
    for year in all_years: 

        print(f'Processing year {year}...')
   
        if os.path.isfile(f'{write_path}/{year}.h5'):
            print(f'{write_path} exists, skipping year {year}...')
            break
        else:
            print(f'{write_path}/{year}.h5 does not exist, creating file...')
            outfile = h5py.File(f'{write_path}/{year}.h5', 'a')
        
        params_ds = outfile.create_dataset("params", shape=len(h5params), dtype=h5py.string_dtype())
        params_ds[:] = h5params

        dt = config["dt"]

        if is_leap_year(int(year)):
            no_of_hours = 366 * 24 / dt
        else:
            no_of_hours = 365 * 24 / dt
        data_ds = outfile.create_dataset("fields", (no_of_hours, len(h5params), 721, 1440))

        selected_hours = list(filter(lambda hour: hour % dt ==0, range(0, 24)))

        files = []
        for nc_file in nc_files:
            if nc_file.startswith(str(year)) and nc_file.endswith(".nc"):
                files.append(nc_file)
        print(f'Number of files for the year {year}: {len(files)}')

        # pl_params files are by day (1 day 1 file)
        # for param in random.sample(config["pl_params"], 3):
        for param in config["pl_params"]:

            selected_files = list(filter(lambda file: f'-{param}-' in file, files))
            selected_files.sort()
            # print(f'Number of files for the param {param}: {len(selected_files)}')
            # print(f'Files for parameter {param}: {selected_files}')

            # for file in random.sample(selected_files, 1):
            for file in selected_files:

                print(f'\tProcessing file: {file}...')
                f = h5py.File(f'{data_path}/{file}', 'r')

                start_date, end_date = get_file_date(file)
                start_month = int(start_date[0:2])
                start_day = int(start_date[2:4])

                keys = list(f.keys())
                data_key = keys[0]

                pressure_level_keys = {}
                for level in range(np.shape(f["level"])[0]):
                    pressure_level_keys[int(f["level"][int(level)])] = int(level)
                desired_pressure_levels = config["pressure_levels"][data_key.lower()]

                for hour in selected_hours:

                    hour_index = get_hour_index(int(year), start_month, start_day, hour, dt)
                    
                    for desired_pressure_level in desired_pressure_levels:
                    
                        data = f[data_key][hour][pressure_level_keys[desired_pressure_level]]
                        param_index = h5params.index(f'{param}{desired_pressure_level}')
                        # print(f'hour index: {hour_index} for {year}-{start_month}-{start_day}-{hour}')
                        # print(f'param index: {param_index} for {param}{desired_pressure_level}')
                        data_ds[int(hour_index), param_index] = data

        # sfc_params files are by month (1 month 1 file)
        # for param in random.sample(config["sfc_params"],3):
        for param in config["sfc_params"]:

            selected_files = list(filter(lambda file: f'-{param}-' in file, files))
            selected_files.sort()
            # print(f'Number of files for the param {param}: {len(selected_files)}')
            # print(f'Files for parameter {param}: {selected_files}')

            # for file in random.sample(selected_files,1):
            for file in selected_files:

                print(f'\tProcessing file: {file}...')
                f = h5py.File(f'{data_path}/{file}', 'r')

                start_date, end_date = get_file_date(file)
                start_month = int(start_date[0:2])

                keys = list(f.keys())
                data_key = keys[0]

                no_of_days = get_days_in_month(start_month)
                if is_leap_year(int(year)) and start_month == 2:
                    no_of_days +=1
                    
                for day in range(1, no_of_days + 1):

                    for hour in selected_hours:

                        infile_hour_index = (day-1) * 24 + hour
                        # print(f'infile hour index: {infile_hour_index} for day: {day}, hour: {hour}')
                        
                        outfile_hour_index = get_hour_index(int(year), start_month, int(day), hour, dt)
                        data = f[data_key][infile_hour_index]
                        param_index = h5params.index(f'{param}')
                        # print(f'hour index: {outfile_hour_index} for {year}-{start_month}-{day}-{hour}')
                        # print(f'param index: {param_index} for {param}')
                        data_ds[outfile_hour_index, param_index] = data

        print(f'Closing file {year}.h5...')
        outfile.close()


if __name__ == "__main__":
    main()
