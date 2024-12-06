VENV=~/.venv/website-wagtail/bin/activate

init:
	python3 -m venv ~/.venv/website-wagtail

check:
	. $(VENV) && python manage.py check
	. $(VENV) && python manage.py check --tag models --tag compatibility
	. $(VENV) && python manage.py check --database default 

migratecheck: # doesn't seem to work?
	. $(VENV) && python manage.py sqlmigrate

makemigrations:
	. $(VENV) && python manage.py makemigrations

showmigrations:
	. $(VENV) && python manage.py showmigrations

sqlmigrate:
	. $(VENV) && python manage.py sqlmigrate $(name) 0001

migrate:
	. $(VENV) && python manage.py migrate

run:
	. $(VENV) && python manage.py runserver

setup: init
	. $(VENV) && pip install --upgrade pip
	. $(VENV) && pip install -r website/requirements.txt

superuser:
	. $(VENV) && python manage.py createsuperuser --noinput --username "admin" --email "ustcemail@somedomain.com"

resetadminpassword:
	. $(VENV) && python manage.py reset_admin_password
