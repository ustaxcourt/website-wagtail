VENV=~/.venv/website-wagtail/bin/activate

init:
	python3 -m venv ~/.venv/website-wagtail

check:
	. $(VENV) && cd website && python manage.py check
	. $(VENV) && cd website && python manage.py check --tag models --tag compatibility
	. $(VENV) && cd website && python manage.py check --database default 

migratecheck:
	. $(VENV) && cd website && python manage.py sqlmigrate

makemigrate:
	. $(VENV) && cd website && python manage.py makemigrations

showmigrations:
	. $(VENV) && cd website && python manage.py showmigrations

sqlmigrate:
	. $(VENV) && cd website && python manage.py sqlmigrate $(name) 0001

migrate:
	. $(VENV) && cd website && python manage.py migrate

run:
	. $(VENV) && cd website && python manage.py runserver

setup: init
	. $(VENV) && pip install --upgrade pip
	. $(VENV) && pip install -r website/requirements.txt

superuser:
	. $(VENV) && cd website && python manage.py createsuperuser --noinput --username "admin" --email "ustcemail@somedomain.com"

resetadminpassword:
	. $(VENV) && cd website && python manage.py reset_admin_password