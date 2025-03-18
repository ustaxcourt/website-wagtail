# 9. Wagtail Upgrade Process

Date: 2025-03-10

## Status

Accepted

## Context

We need a reliable, low-risk process for upgrading Wagtail. This ADR summarizes the key considerations, testing procedures, and best practices drawn from the official Wagtail documentation.

## Items to Consider Before Upgrading

1. **Backups**: Always back up the database before upgrade.
2. **Dependency Review**: Check Wagtail’s compatibility with your Python/Django versions. Upgrade those separately if needed.
3. **Deprecation Warnings**: Consider resolving existing warnings to avoid surprise depcrecations/error.
4. **Third-Party Plugins**: Confirm that plugins are compatible with the target Wagtail release or have updated versions.
5. **Environment Setup**: Follow the usual deployment to test/staging environment that mirrors production as closely as possible. Use a dedicated Github branch.
6. **Test Coverage**: Ensure the unit test suite is passing on the current version before upgrading.

## Reading & Assessing the Upgrade

- **Release Type**: Determine if it’s a patch, minor, or major release. Major releases often remove deprecated features.
- **Release Notes**: Read carefully for breaking changes, new dependencies, and upgrade instructions.
- **Database Migrations**: Note schema changes and confirm your project can apply them without conflicts.

## Testing & Validation

1. **Local Upgrade**: Update Wagtail, install dependencies, run migrations, and smoke-test the site.
2. **Run Automated Tests**: Ensure unit and integration tests pass; watch for new deprecation warnings.
3. **Staging Deployment**: Apply migrations and perform manual QA (especially in the admin). Have content editors test existing key features to ensure they are not broken.
4. **CI/CD Integration**: Use continuous integration to catch any regressions early and confirm the code is production-ready.
5. **Performance/Load Testing** (Optional step): Verify that the new version meets performance standards under expected load.

## Warnings & Errors to Monitor

- **Deprecation Warnings** (e.g., `RemovedInWagtailXWarning`)
- **Migration Conflicts** (schema or data issues)
- **Dependency Version Conflicts** (especially Django/Python mismatches)
- **Runtime/Template Errors** (missing imports, changed APIs, or broken admin UI)
- **Static Files/Asset Issues** (clear cache and run `collectstatic`)

## Best Practices

- **Incremental Upgrades**: Upgrade one Wagtail version at a time if you’re behind multiple releases.
- **Isolate Changes**: Avoid upgrading Django/Python simultaneously—do each step independently.
- **Maintain Environment Parity**: Use the same versions and configs in development, staging, and production.
- **Rollback Strategy**: Keep a backup, tag the old code, and have a plan to revert if necessary.
- **Post-Upgrade Monitoring**: Watch logs and analytics after going live for quick issue detection.
- **Frequent Updates**: Keep Wagtail relatively current to avoid large, disruptive jumps.

## Decision

Adopt this structured, incremental upgrade approach. This reduces risk, ensures thorough testing, and allows quick rollback if needed. By reading the official release notes, fixing deprecations first, and using a staging environment for validation, we maintain a stable and up-to-date Wagtail installation for our project.

> [!IMPORTANT]
> - Update only one version of Wagtail.
> - Security updates/fixes are exception.
> - No other upgrades clubbed with Wagtail version change.
> - Backup database before upgrade.
> - Test locally, and test in sandbox/dev before production.
> - Login to Admin interface to ensure features work.


### Referemce documents

- Read: https://docs.wagtail.org/en/stable/releases/upgrading.html
- Read: https://docs.wagtail.org/en/stable/contributing/release_process.html
- Read: https://docs.wagtail.org/en/stable/releases/upgrading.html#compatible-django-python-versions
