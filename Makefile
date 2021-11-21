create_venv:
	python3 -m venv venv

freeze:
	pip3 freeze > requirements.txt

install:
	pip3 install -r requirements.txt

run:
	FLASK_ENV=development python3 main.py
