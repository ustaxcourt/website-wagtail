# 21. Files to be tested whenever there is an upgrade from one version of wagtail to the next

# Context

To ensure our code is working correctly, whenever there is an upgrade we must test the following files to ensure nothing has broken
and the website still runs as expected.

# Files to be tested

website/home/templates/wagtailadmin/generic/revisions/compare.html
From: .venv/lib/python3.12/site-packages/wagtail/admin/templates/wagtailadmin/generic/revisions/compare.html

website/home/templates/wagtailadmin/home/user_objects_in_workflow_moderation.html
From: .venv/lib/python3.12/site-packages/wagtail/admin/templates/wagtailadmin/home/user_objects_in_workflow_moderation.html

website/home/templates/wagtailadmin/home/workflow_objects_to_moderate.html
From: .venv/lib/python3.12/site-packages/wagtail/admin/templates/wagtailadmin/home/workflow_objects_to_moderate.html

website/home/templates/wagtailadmin/login.html
From: .venv/lib/python3.12/site-packages/wagtail/admin/templates/wagtailadmin/login.html
