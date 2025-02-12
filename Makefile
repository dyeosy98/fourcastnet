venv:
	python -m venv venv

install:
	pip install -r requirements.txt

download:
	python download.py

format:
	python format.py
