VENV=../.venv/bin/activate

init:
	python -m venv ../.venv

cmd:
	. $(VENV) && $(c)

check:
	. $(VENV) && python manage.py check
	. $(VENV) && python manage.py check --tag models --tag compatibility
	. $(VENV) && python manage.py check --database default
	. $(VENV) && ruff check
	. $(VENV) && djlint . --lint

format:
	. $(VENV) && ruff format
	. $(VENV) && djlint . --reformat --format-css --format-js

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
	. $(VENV) && coverage html -d coverage_html && open coverage_html/index.html

test-e2e:
	npx cypress run --browser chrome

cypress-open:
	npx cypress open --browser chrome

pytest:
	. $(VENV) && pytest

sqlmigrate:
	. $(VENV) && python manage.py sqlmigrate $(name) $(id)

migrate:
	. $(VENV) && python manage.py migrate

rmdb:
	rm ./db.sqlite3 || echo "Local DB file already deleted"

rmmedia:
	rm -rf ./media || echo "Media folder already deleted"

resetdb: rmdb rmmedia makemigrations migrate superuser createpages

reset: setup resetdb

run:
	. $(VENV) && python manage.py runserver

setup: init
	. $(VENV) && pip install --upgrade pip
	. $(VENV) && pip install -r requirements.txt
	npm install
	npx gulp init
	npx gulp compile

superuser:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} DJANGO_SUPERUSER_PASSWORD=$${password:-ustcAdminPW!} python manage.py createsuperuser --noinput --username "admin" --email "ustcemail@somedomain.com"

users:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py create_users --group_name $${group:-"Editors"}

resetadminpassword:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py reset_admin_password

# an idempotent command for creating the pages after all the models / migrations have finished running
createpages:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py create_pages
