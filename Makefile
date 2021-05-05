install:
	pip install -r requirements.txt

test:
	python -m pytest -vv

lint:
	pylint --disable=R,C main.py census.py covid.py  tests

venv_create: 
	python -m venv ..\.venv

venv_activate:
	.\..\.venv\Scripts\activate

venv: venv_create venv_activate

all: install lint test