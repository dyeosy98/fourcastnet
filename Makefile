activate:
	source venv/bin/activate

install:
	pip install -r requirements.txt

download:
	python get-era5-data/download.py

