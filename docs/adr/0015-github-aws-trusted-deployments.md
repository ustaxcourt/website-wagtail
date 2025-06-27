## ADR-0015: Secure Production Deployments using AWS OIDC and GitHub Environments

Date: 2025-06-27

## Status

Accepted

### Context

The current production deployment process relies on long-lived IAM user credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) stored as GitHub secrets. This presents security issues.

Our goal is to migrate to a more secure, keyless, and auditable deployment model that enforces a strict separation of duties and a clear approval process.

### Decision

We will adopt a multi-layered security strategy that eliminates static credentials and enforces cryptographic and manual verifications for all production deployments.

1.  **Eliminate Static Credentials:** We will permanently remove the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from GitHub secrets.
2.  **Adopt AWS OIDC:** We will use OpenID Connect (OIDC) to establish a trust relationship between our production AWS account and the GitHub Actions runner. Workflows will assume an IAM Role by exchanging a short-lived OIDC token for temporary AWS credentials.
3.  **Implement GitHub Environments:** Deployments to `production` environment will require manual approval from designated reviewers and will be restricted to a specific branch.

This approach ensures that a production deployment can only be triggered from the correct branch, after the workflow's integrity is verified, and only after an authorized user explicitly approves the run.

### Consequences

**Positive:**

  * **Enhanced Security:** The attack surface is drastically reduced by eliminating long-lived secrets. Credentials are now temporary and scoped to a single workflow run.
  * **Improved Auditability:** All production deployment approvals are explicitly logged in GitHub, providing a clear audit trail of who authorized what and when.
  * **Foolproof Authorization:** The OIDC trust policy's conditions (checking the repository and environment) provide cryptographic verification controlled in AWS, cannot be bypassed, even by repository administrators.
  * **Reduced Human Error:** The manual and error-prone step of managing secrets before a deploy is completely eliminated.

**Negative:**

  * **Increased Initial Complexity:** Requires a one-time configuration of the OIDC provider and a specific IAM Role in AWS.
  * **Process Change:** Deployments now involve a formal approval step within the GitHub UI, which developers need to be aware of.

-----

### Implementation Plan for Production

These steps should be performed in sequence to configure the production environment.

### Part 1: AWS Production Account Configuration

1.  **Create the OIDC Identity Provider (One-time setup)**

      * In the AWS Console, navigate to **IAM \> Identity providers**.
      * Click **Add provider**.
      * **Provider type:** `OpenID Connect`
      * **Provider URL:** `https://token.actions.githubusercontent.com`
      * **Audience:** `sts.amazonaws.com`
      * Click **Add provider**.

2.  **Create the Production IAM Role**

      * In the AWS Console, navigate to **IAM \> Roles** and click **Create role**.
      * **Trusted entity type:** Select **Web identity**.
      * **Identity provider:** Choose the `token.actions.githubusercontent.com` provider you just created.
      * **Audience:** Choose `sts.amazonaws.com` and click **Next**.
      * **Add permissions:** Attach the necessary IAM policies that allow your workflow to perform its tasks (e.g., Terraform apply, ECS service updates, CloudFront invalidation).
      * **Name and review:**
          * **Role name:** `github-workflow-deployer`
          * **Description:** This is a new IAM role to be used for all Github deployments.
      * Click **Create role**.

3.  **Configure the Role's Trust Policy**

      * Navigate to the `github-workflow-deployer`.
      * Select the "Permissions" tab, add the existing `"deployer"` policy.
      * Select the **Trust relationships** tab and click **Edit trust policy**.
      * **Replace the entire content** with the following JSON. This is the most critical step, as it locks the role to your repository and the `production` environment.

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Federated": "arn:aws:iam::<Production-Account-ID>:oidc-provider/token.actions.githubusercontent.com"
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                        "token.actions.githubusercontent.com:sub": "repo:ustaxcourt/website-wagtail:environment:production"
                    }
                }
            }
        ]
    }
    ```

### Part 2: GitHub Repository Configuration

1.  **Configure the `production` Environment**

      * In your repository, navigate to **Settings \> Environments** `production`.
      * Click **Configure environment**.
      * Under **Protection rules**, configure the following:
          * **Required reviewers:** Check this box and add the authorized team or individuals (e.g., `@ustaxcourt/administrators`).
          * **Deployment branches:** Check this box, select **Selected branches**, and add `main` as the only allowed branch.

2.  **Configure Branch Protection for `main`**

      * Navigate to **Settings \> Branches** and click **Add rule** for the `main` branch (or edit the existing one).
      * Enable the following protections:
          * `[x]` **Require a pull request before merging**
          * `[x]` **Require approvals** (Set to at least 1)
          * `[x]` **Require review from Code Owners**
          * `[x]` **Dismiss stale pull request approvals when new commits are pushed**
          * `[x]` **Include administrators**
