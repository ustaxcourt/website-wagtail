# Code Styles
This is a collection of code styles for Python, Django, Testing and IaC. This is a work in progress document and we intend to keep it updated.

## Python

Setting up Django project.

https://github.com/cookiecutter/cookiecutter-django?tab=readme-ov-file

### Django
In Django, business logic should live in:

- Services - functions, that mostly take care of writing things to the database. Services are where business logic lives.
- Selectors - functions, that mostly take care of fetching things from the database.
- Model properties (with some exceptions). Models should take care of the data model and not much else.
- Model clean method for additional validations (with some exceptions). If you can do validation using Django's constraints, then you should aim for that.

#### Testing
- Models need to be tested only if there's something additional to them - like validation, properties or methods.
- Testing should be done using pytest.
- Test files should be named `test_<module>.py`.
- Test classes should be named `Test<Module>`.
- Test methods should be named `test_<method>`.

### Naming Conventions

- Use `lower_case_with_underscores` for function names, variable names, and attribute names.
- Use `UpperCaseWithUnderscores` for class names.
- Service we use the naming convention: `<entity>_<action>`, example: `user_create()`.
- APIs we use the following naming convention: `<Entity><Action>Api`, example: `UserCreateApi`.

## Reference
1. Django specific coding style recommendations from: Hacksoft Django Styleguide: https://github.com/HackSoftware/Django-Styleguide
2. For Python, Django, Testing and Terraform, recommendations from: Kraken Technologies coding conventions: https://github.com/octoenergy/public-conventions?tab=readme-ov-file

