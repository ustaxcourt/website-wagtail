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

reset:
	. $(VENV) && rm ./db.sqlite3 || echo "file already deleted"
	make migrate

run:
	. $(VENV) && python manage.py runserver

setup: init
	. $(VENV) && pip install --upgrade pip
	. $(VENV) && pip install -r requirements.txt
	npm install
	npx gulp init
	npx gulp compile

superuser:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.dev} DJANGO_SUPERUSER_PASSWORD=$${password:-ustcAdminPW!} python manage.py createsuperuser --noinput --username "admin" --email "ustcemail@somedomain.com"

export DJANGO_SUPERUSER_PASSWORD=$(SUPERUSER_PASSWORD)
resetadminpassword:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.dev} python manage.py reset_admin_password
