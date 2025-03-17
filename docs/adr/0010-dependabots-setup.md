# 10. Best Practices for GitHub Dependabot Alerts and PR Merges

Date: 2025-03-17

## Status

Accepted

## Context

The Wagtail CMS project uses Python (pip) and Node.js (NPM) dependencies. GitHub Dependabot automates discovery of outdated or vulnerable packages. Our existing unit tests cover most pages but not all of Wagtail’s admin interface. Major version bumps are particularly risky. We require manual review on all Dependabot PRs to mitigate potential breakage on Admin interface.

## Best Practices

- **Regularly Review and Merge Updates:** Promptly address Dependabot pull requests to stay current with patches and improvements. Delays can lead to larger, riskier upgrades later.
- **Maintain Comprehensive Test Coverage:** Automated tests are essential but should be supplemented by manual checks, especially for major version updates. This helps prevent breakage in critical or less-tested components like the Wagtail admin interface.
- **Prioritize Security Alerts:** Security-related updates should be merged sooner rather than later, but still undergo a careful review to confirm compatibility and stability.
- **Document and Track Changes:** Use meaningful commit messages, release notes, and version tracking. This helps the team quickly identify changes, revert problematic updates, or replicate fixes across other environments.

## Decision

- Manually review all Dependabot pull requests.
- No major version updates will be merged without proper testing on Admin interface.
- Security updates are prioritized but also require a review. We prohibit automerging to ensure a human checks compatibility and safety.

These guidelines reduce risks while keeping dependencies current.

## Consequence

We benefit from improved dependency hygiene and timely security patches. Manual review reduces the chances of introducing breaking changes or untested features. However, this approach increases maintenance effort and requires consistent reviewer availability. Ultimately, the disciplined process leads to a more stable, secure project.
