venv:
	python -m venv venv
	pip install -r requirements.txt

install:
	pip install -r requirements.txt

download:
	python download.py

format:
	python format.py
