init:
	python3 -m venv ~/.venv/website-wagtail
	source ~/.venv/website-wagtail/bin/activate

migratecheck:
	cd website && python manage.py sqlmigrate

makemigrate:
	cd website && python manage.py makemigrations

migrate:
	cd website && python manage.py migrate

run:
	cd website && python manage.py runserver

setup:
	pip install --upgrade pip
	pip install -r website/requirements.txt
