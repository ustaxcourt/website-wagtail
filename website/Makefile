VENV=~/.venv/website-wagtail/bin/activate

init:
	python -m venv ~/.venv/website-wagtail

check:
	. $(VENV) && python manage.py check
	. $(VENV) && python manage.py check --tag models --tag compatibility
	. $(VENV) && python manage.py check --database default
	. $(VENV) && ruff check

format:
	. $(VENV) && ruff format

fix:
	. $(VENV) && ruff check --fix

typecheck:
	. $(VENV) && mypy .

precommit:
	. $(VENV) && pre-commit sample-config && pre-commit run --all-files

migratecheck:
	. $(VENV) && python manage.py sqlmigrate $(name) $(id)

makemigrations:
	. $(VENV) && python manage.py makemigrations

showmigrations:
	. $(VENV) && python manage.py showmigrations

coverage:
	. $(VENV) && coverage run -m pytest
	. $(VENV) && coverage report

test-e2e:
	npx cypress run --browser chrome

pytest:
	. $(VENV) && pytest

sqlmigrate:
	. $(VENV) && python manage.py sqlmigrate $(name) $(id)

migrate:
	. $(VENV) && python manage.py migrate

rmdb:
	rm ./db.sqlite3 || echo "Local DB file already deleted"

reset: rmdb setup makemigrations migrate superuser users

run:
	. $(VENV) && python manage.py runserver

setup: init
	. $(VENV) && pip install --upgrade pip
	. $(VENV) && pip install -r requirements.txt
	npm install
	npx gulp init
	npx gulp compile

superuser:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.dev} DJANGO_SUPERUSER_PASSWORD=$${password:-ustcAdminPustcAdminPWW!} python manage.py createsuperuser --noinput --username "admin" --email "ustcemail@somedomain.com"

users:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.dev} python manage.py create_users --group_name $${group:-"Editors"}

resetadminpassword:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.dev} python manage.py reset_admin_password
