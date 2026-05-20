# Code Styles

This is a collection of code styles for Python, Django, Testing and IaC. This is a work in progress document and we intend to keep it updated.

## Python

We use Python version [3.12](https://peps.python.org/pep-0693/).

### Requirements

Requirements are installed using `pip`. Local/development requirements go to `local.txt` and production requirements can go to `base.txt`.

### Django

- Services - functions, that mostly take care of writing things to the database. Services are where business logic lives.
- Selectors - functions, that mostly take care of fetching things from the database.
- Model properties (with some exceptions). Models should take care of the data model and not much else.
- Model clean method for additional validations (with some exceptions). If you can do validation using Django's constraints, then you should aim for that.

#### Testing

- Models need to be tested only if there's something additional to them - like validation, properties or methods.
- General [test naming conventions](https://github.com/HackSoftware/Django-Styleguide?tab=readme-ov-file#testing-2).
- Testing should be done using pytest, pytest-django.
- Test files should be named `test_<module>.py`.
- Test classes should be named `Test<Module>`.
- Test methods should be named `test_<method>`.

### Naming Conventions

- Use `lower_case_with_underscores` for function names, variable names, and attribute names.
- Use `UpperCaseWithoutUnderscores` for class names.
- Service we use the naming convention: `<entity>_<action>`, example: `user_create()`.
- APIs we use the following naming convention: `<Entity><Action>Api`, example: `UserCreateApi`.

## Developer Experience

- Typing: [mypy](https://www.mypy-lang.org/).
- Linting and Formating: [ruff](https://github.com/astral-sh/ruff), usage: https://github.com/astral-sh/ruff?tab=readme-ov-file#usage.
- Configure [pre-commit hooks](https://github.com/HackSoftware/Django-Styleguide-Example/blob/master/.pre-commit-config.yaml) to run on every code commit/push.

## Terraform

See: https://github.com/octoenergy/public-conventions/blob/main/conventions/terraform.md

## Git Naming Conventions

We are using Jira (https://ustaxcourt-team.atlassian.net/browse/WAG) as an issue tracking system for project management. In order to get better metrics for performance and connect the code with the issues, we are requiring the following naming conventions for branches and pull requests:

### Branch Names

Please use a branch name that includes the Issue ID in the name. **It must be uppercase** for it to properly link to the issue. For example, if the Issue ID is "WAG-123" then the branch name should begin with "WAG-123-..." After that please use a brief summary of the work that the branch will do.

### Pull Request Titles

Please reference the Issue ID in the Title or Description of any pull request. This way the Github integration will automatically connect a task in Jira with the Pull Request. Again, **it must be uppercase**. This will give us better insights and help drive decision making. For example, when you create a PR, please give it the title "Introduce Git Naming Conventions - WAG-375" or mention it in the description.

## Reference

1. Django specific coding style recommendations from: Hacksoft Django Styleguide: https://github.com/HackSoftware/Django-Styleguide
2. For Python, Django, Testing and Terraform, recommendations from: Kraken Technologies coding conventions: https://github.com/octoenergy/public-conventions?tab=readme-ov-file
3. Wagtail getting started, from: https://docs.wagtail.org/en/stable/getting_started/tutorial.html
