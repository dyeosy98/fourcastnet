import boto3
import botocore
from botocore import UNSIGNED
from botocore.config import Config
import os
import yaml

def main():

    # Initialize config
    #print("Initializing config...")
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Initialize years
    #print("Initializing years...")
    train_years = list(range(config["start_train_year"], config["end_train_year"] + 1))
    test_years = config["test_years"]
    out_of_sample_years = config["out_of_sample_years"]

    all_years = train_years + test_years + out_of_sample_years

    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

    # Initialize s3 client
    #print("Initializing s3 client...")
    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))

    # Get list of relevant objects
    print("Getting list of objects to be downloaded...")
    objects_to_download = []

    for year in all_years:
        for month in months:
            objects = s3_client.list_objects(Bucket=config["bucket_name"], Prefix=f'{config["pl_folder"]}/{year}{month}/{config["pl_folder"]}')
            for obj in objects["Contents"]:
                object_key = obj["Key"]
                if any(f'_{param}.' in object_key for param in config["pl_params"]):
                    obj_path = f'{config["download_path"]}/{year}-{month}-{object_key.replace("/", "-").split(".")[7].split("_")[-1]}-{object_key.replace("/", "-").split(".")[9]}.nc'
                    if os.path.exists(obj_path):
                        print(f'{obj_path} already exists, skipping download')
                    else: 
                        print(f'Downloading {object_key} as {obj_path}')
                        try: 
                            s3_client.download_file(config["bucket_name"], object_key, obj_path)
                        except botocore.exceptions.ClientError as e:
                            if e.response['Error']['Code'] == "404":
                                print(f'The object {object_key} does not exist.')
                            else:
                                raise
                
    for year in all_years:
        for month in months:
            objects = s3_client.list_objects(Bucket=config["bucket_name"], Prefix=f'{config["sfc_folder"]}/{year}{month}/{config["sfc_folder"]}')
            for obj in objects["Contents"]:
                object_key = obj["Key"]
                if any(f'_{param}.' in object_key for param in config["sfc_params"]):
                    obj_path = f'{config["download_path"]}/{year}-{month}-{object_key.replace("/", "-").split(".")[7].split("_")[-1]}-{object_key.replace("/", "-").split(".")[9]}.nc'
                    if os.path.exists(obj_path):
                        print(f'{obj_path} already exists, skipping download')
                    else: 
                        print(f'Downloading {object_key} as {obj_path}')
                        try: 
                            s3_client.download_file(config["bucket_name"], object_key, obj_path)
                        except botocore.exceptions.ClientError as e:
                            if e.response['Error']['Code'] == "404":
                                print(f'The object {object_key} does not exist.')
                            else:
                                raise

    print(objects_to_download)

if __name__ == "__main__":
    main()
