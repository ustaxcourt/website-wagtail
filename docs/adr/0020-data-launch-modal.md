# Details on the deletion of the data-launch-modal variable in website/home/templates/wagtailadmin/home/workflow_objects_to_moderate.html

Also deleted in website/home/templates/wagtailadmin/generic/revisions/compare.html

Date: 2025-11-24

## Status

We’ve currently accepted that deleting the variable is the best course of action and plan on returning to it, if Wagtail decides to update their template in the virtual environment since the file we changed was overridden from there.


## Context

The variable we found was removed and that solved the problem, but we were unsure if the variable handled more than what we were looking to remove. Attempts to find details on it were unsuccessful.

The closest we came to finding out what is going on in the workflow is this: https://github.com/wagtail/wagtail/blob/3ae5870c81b332b6807d30d722bd0b8cf214dd26/client/src/entrypoints/admin/workflow-action.js#L16



Both items below are found in the .venv

The generated modal:
wagtail/admin/templates/wagtailadmin/shared/workflow_action_modal.html



The class used in our Form:
wagtail/forms.py
class TaskStateCommentForm(forms.Form)
