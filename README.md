## Data Download and Pre-Processing for Running FourCastNet on AWS

This repository contains code for downloading [NSF NCAR Curated ECMWF Reanalysis 5 (ERA5)](https://registry.opendata.aws/nsf-ncar-era5/) data via the [Registry of Open Data on AWS](https://registry.opendata.aws/) and pre-processing it for training the FourCastNet model.  

### Existing Methods
The NVIDIA Modulus Launch GitHub repository [here](https://github.com/NVIDIA/modulus-launch/tree/main/examples/weather/dataset_download) states that a subset of the data is available [via Globus](https://app.globus.org/file-manager?origin_id=945b3c9e-0f8c-11ed-8daf-9f359c660fbd&origin_path=%2F~%2Fdata%2F). If you have access to the AWS S3 Connector on Globus, downloading the sample data from Globus may be a simpler method. 

The NVIDIA Modulus Launch GitHub repository [here](https://github.com/NVIDIA/modulus-launch/tree/main/examples/weather/dataset_download) also provides a script for downloading and pre-processing data. However, there may be memory management issues when running in a Docker container as recommended by the documentation, and checkpointing is also an issue as the downloading and pre-processing durations are long. 

**The scripts in this repository are meant to be run directly on an Amazon EC2 instance.**

### Requirements
- Amazon EC2 instance 
- File system with at least XX TB capacity
- Python 3

The scripts have been tested on an Amazon EC2 c6a.4xlarge instance, with an Amazon Elastic File System (EFS) mounted.

## Using this Repository

### Pre-requisites

1. Clone the repository from your EC2 instance: `git clone https://github.com/dyeosy98/fourcastnet.git`

2. Create a virtual environment and install requirements: `make up`

3. Activate the virtual environment: `source venv/bin/activate`

### Download data and format it

4. Edit **config.yaml** accordingly, especially with the `download_path` variable.

5. Download the data: `make download`.

    - The **download.py** script gets all relevant data as dictated by **config.yaml**.

    - One year's worth of data per the default **config.yaml** settings amounts to around 2.45 TiB, and can take almost 8 hours to be downloaded.

6. Extract the relevant data: `make format`.
    
    - The **format.py** script processes data by year and produces 1 .h5 file per year (e.g. 2010.h5, 2011.h5). 
    
    - It takes around 8 hours to process one year's worth of data, amounting to around 190 GB per .h5 file. 

    - If the script identifies that the .h5 file for a year already exists, it will skip processing that year's data. Therefore, if the script is interrupted midway through processing one year's data, the partial file should be deleted before running the script again.

### Run Training

7. Start compute node: `srun -N --pty /bin/bash -il`

8. 