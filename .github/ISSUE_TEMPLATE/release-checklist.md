---
name: "Release Checklist"
about: "Checklist for a release in the Python + AWS + Wagtail/Django project"
title: "[Release] - <Version or Release Name>"
labels: ["release", "checklist", "technical"]
assignees: []
---

# Release Checklist

Use this checklist to ensure all necessary tasks are completed before deploying Django/Wagtail project to AWS.

## 1. Pre-Release

- [ ] **Changelog**
  - Prepare/Review/Update changelog (or release notes).
  - Document all relevant changes (features, fixes, improvements).

- [ ] **Dependency Review**
  - Review Python packages in `requirements.txt`.
  - Update and test any out-of-date or vulnerable packages.
  - Ensure pinned versions are correct if needed.

- [ ] **Tests**
  - Confirm all tests pass (CI green).
  - Check code coverage meets required thresholds.

- [ ] **Lint & Static Analysis**
  - Confirm codebase passes ruff, flake8, black, isort (or equivalent).
  - Address any code quality warnings or style issues.

---

## 2. Infrastructure Checks (AWS)

- [ ] **Infrastructure as Code**
  - Using Terraform, ensure changes for this release are planned and applied to the correct pre-production environment. Look for any errors/warnings in the deployment log.
  - Check for unexpected infrastructure drift.

- [ ] **Secrets & Environment Variables**
  - Verify that any new environment variables are set (e.g., in AWS SSM Parameter Store, Secrets Manager).
  - Ensure secrets (like database credentials) are properly stored and encrypted.

- [ ] **AWS Services**
  - For using Docker/ECR/ECS, confirm new container images are built, pushed, and tested.
  - For EC2-based hosting, confirm new AMI or configurations are in place.
  - Check logs in AWS CloudWatch for errors in staging/pre-production.

- [ ] **Scaling / Load Testing** (if applicable)
  - Perform load or stress testing if it’s a major release or expected high traffic.
  - Verify auto-scaling settings are valid.

---

## 3. Django & Wagtail Deployment Checklist

This section includes key points from the [Django 5.2 Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/) **plus** Wagtail considerations:

### 3.1 Security-Related Settings

- [ ] **DEBUG is OFF**
  - Make sure `DEBUG = False` in your production settings.

- [ ] **Allowed Hosts**
  - Properly configure `ALLOWED_HOSTS` for all your domain(s).

- [ ] **Secret Key**
  - Ensure `SECRET_KEY` is unique, confidential, and not committed to source control (use environment variables or AWS Secrets Manager).

- [ ] **SSL / HTTPS**
  - Confirm HTTPS is enforced.
  - Check redirects from HTTP to HTTPS at load balancer or server level.

- [ ] **CSRF & Session Settings**
  - Confirm `CSRF_COOKIE_SECURE` and `SESSION_COOKIE_SECURE` are set to `True` for HTTPS.
  - Consider using `CSRF_TRUSTED_ORIGINS` for known domains.

- [ ] **Security Middleware**
  - Ensure `X-Frame-Options` is properly set (e.g., `SAMEORIGIN` for Wagtail).
  - Check if `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, and other relevant middleware settings are configured.

- [ ] **File Permissions & Ownership**
  - Verify the application user does not have unnecessary write privileges.
  - Lock down any sensitive directories.

- [ ] **Logging & Error Reporting**
  - Confirm error logging is set up for production (e.g., Sentry, AWS CloudWatch, or similar).
  - Ensure debug logs are not publicly visible.

### 3.2 Database & Migrations

- [ ] **Database Backup**
  - Ensure a recent RDS database backup snapshot had completed successfully.

- [ ] **Migrations**
  - Run `manage.py makemigrations` and `manage.py migrate` in a test environment to ensure DB changes are valid.
  - Check backward compatibility if partial rollbacks might be needed.

- [ ] **Database Security**
  - Ensure DB credentials are properly stored (AWS RDS, for example).
  - Restrict DB access to necessary hosts/security groups.

### 3.3 Wagtail-Specific Checks

- [ ] **Admin & Page Models**
  - Confirm new Wagtail page models, admin features, or content blocks function as expected.
  - Check for permission settings for new or changed Wagtail admin features.

- [ ] **Static / Media Files**
  - Run `collectstatic` to gather static files for production.
  - Verify media uploads are served correctly from the designated storage (S3, local, etc.).

---

## 4. Final Confirmation

- [ ] **Documentation**
  - Update READMEs, wiki, or inline docs for any new features or config instructions.

- [ ] **Smoke Test (Staging / Pre-Production)**
  - Deploy the release candidate to staging.
  - Perform a quick end-to-end check:
    - User login/auth.
    - Major Wagtail admin tasks.
    - Critical routes or APIs.
    - AWS logs/metrics for any immediate errors.

- [ ] **Technical Sign Off**
  - Team lead, QA, or product owner approves the staging environment as production-ready.

---

## 5. Production Deployment

- [ ] **Deployment Window & Communication**
  - Schedule or communicate the planned deployment time to relevant teams/stakeholders.
  - Confirm if any downtime or rolling deploy is planned.

- [ ] **Create Git Tag & Release**
  - Identify the commit tag that will be used for Production deployment.

- [ ] **Post-Deployment Verification**
  - Monitor logs (e.g., CloudWatch, Sentry, etc.) for critical errors.
  - Verify key user paths and admin functionality in production.
  - Confirm correct environment settings (no accidental `DEBUG=True`).

- [ ] **Rollback / Hotfix Plan**
  - Make sure the previous stable release is accessible if you need to revert.
  - Document any hotfix procedures if immediate patches are needed.

---

### Additional Notes or Attachments

<details>
<summary>Optional: Extra context or screenshots</summary>

<!-- Add any relevant screenshots, links, or context here -->

</details>
