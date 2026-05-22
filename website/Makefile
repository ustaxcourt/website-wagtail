VENV=../.venv/bin/activate
MIGRATION ?= zero

 .DEFAULT:
	@echo "Falling back to ./website-wagtail/ for '$@'"
	@$(MAKE) -C ../. $@

init:
	python -m venv ../.venv

cmd:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} $(c)

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

check-migrations:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py makemigrations --check --dry-run || { echo "Missing migrations detected. Run 'make makemigrations' and commit the generated file." >&2; exit 1; }

showmigrations:
	. $(VENV) && python manage.py showmigrations

coverage:
	. $(VENV) && coverage run -m pytest
	. $(VENV) && coverage report
	. $(VENV) && coverage html -d coverage_html && open coverage_html/index.html

test-e2e:
	CYPRESS_INCLUDE_ADMIN_VALIDATION=$(if $(filter include-admin,$(args)),true,false) CYPRESS_BASE_URL="$(baseUrl)" CYPRESS_ADMIN_USERNAME="$(value adminUsername)" CYPRESS_ADMIN_PASSWORD="$(value adminPassword)" npx cypress run --browser chrome

test-voiceover:
	PLAYWRIGHT_BASE_URL="$(baseUrl)" npx playwright test --config playwright/playwright.config.ts

test-e2e-aws:
	./scripts/cypress/run_against_aws.sh --mode run \
		$(if $(aws_env),--aws-env $(aws_env),) \
		$(if $(base_url),--base-url $(base_url),) \
		$(if $(secret_id),--secret-id $(secret_id),) \
		$(if $(region),--region $(region),) \
		$(if $(spec),--spec $(spec),) \
		$(if $(browser),--browser $(browser),--browser chrome) \
		$(if $(filter include-admin,$(args)),--include-admin,)

cypress-open:
	CYPRESS_INCLUDE_ADMIN_VALIDATION=$(if $(filter include-admin,$(args)),true,false) CYPRESS_BASE_URL="$(baseUrl)" CYPRESS_ADMIN_USERNAME="$(value adminUsername)" CYPRESS_ADMIN_PASSWORD="$(value adminPassword)" npx cypress open --browser chrome

cypress-open-aws:
	./scripts/cypress/run_against_aws.sh --mode open \
		$(if $(aws_env),--aws-env $(aws_env),) \
		$(if $(base_url),--base-url $(base_url),) \
		$(if $(secret_id),--secret-id $(secret_id),) \
		$(if $(region),--region $(region),) \
		$(if $(spec),--spec $(spec),) \
		$(if $(browser),--browser $(browser),--browser chrome) \
		$(if $(filter include-admin,$(args)),--include-admin,)

pytest:
	. $(VENV) && pytest

sqlmigrate:
	. $(VENV) && python manage.py sqlmigrate $(name) $(id)

migrate:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py migrate

rmdb:
	rm ./db.sqlite3 || echo "Local DB file already deleted"

rmmedia:
	rm -rf ./media || echo "Media folder already deleted"

resetdb: rmdb rmmedia makemigrations migrate superuser createpages updatepages

reset: setup resetdb

updateindex:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py update_index

run:
	. $(VENV) && python manage.py runserver

run-debug:
	. $(VENV) && DJANGO_SETTINGS_MODULE=app.settings.debug python manage.py runserver

cypress-env:
	@test -f cypress.env.json || (echo '{"ADMIN_USERNAME":"admin","ADMIN_PASSWORD":"ustcAdminPW!"}' > cypress.env.json && echo "Created cypress.env.json")

setup-pip: init
	. $(VENV) && pip install --upgrade pip
	. $(VENV) && pip install -r requirements.txt

setup-npm:
	npm install
	npx gulp copyAssets
	npx gulp compile

setup: setup-pip setup-npm cypress-env

superuser:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} DJANGO_SUPERUSER_PASSWORD=$${password:-ustcAdminPW!} python manage.py createsuperuser --noinput --username "admin" --email "webmaster@ustaxcourt.gov"

users:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py create_users --group_name $${group:-"Editors"}

upgrade-test:
	. $(VENV) && PYTHONWARNINGS=always pytest tests --capture=no
	. $(VENV) && python -Wd manage.py runserver

resetadminpassword:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py reset_admin_password

production-checks:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py production_checks

# an idempotent command for creating the pages after all the models / migrations have finished running
createpages:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py create_pages

createlitccitiespage:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py create_litc_cities_page

updatepages:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py update_pages

collectstatic:
	. $(VENV) && python manage.py collectstatic --noinput --clear

preregisterusers:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py preregister_users

preregistersuperusers:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py preregister_superusers

setupses:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py set_up_ses

setupwagtaillroles:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py setup_wagtail_roles

rollbackmigrate:
	. $(VENV) && python manage.py migrate home $(MIGRATION)

rollbackall:
	. $(VENV) && python manage.py migrate home zero

backfillliverevisions:
	. $(VENV) && DJANGO_SETTINGS_MODULE=$${settings:-app.settings.local} python manage.py backfill_live_revisions

get-website-secret:
	. $(VENV) && python ../infra/scripts/get_website_secret.py $(args)

copy-website-secret:
	. $(VENV) && python ../infra/scripts/copy_website_secret.py $(args)

add-preregister-user:
	. $(VENV) && python ../infra/scripts/add_preregister_user.py $(args)
