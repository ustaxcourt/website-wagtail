## Support Documentation: PRODUCTION Deploy Workflow

This document provides guidance on how to use the `PRODUCTION Deploy` GitHub workflow to deploy code changes to the production environment.

### Purpose

The `PRODUCTION Deploy` workflow automates the process of deploying a specific commit to the production environment. It includes checks for authorized deployers, sets up the necessary environment, deploys infrastructure changes using Terraform, runs database migrations, updates the ECS service, and invalidates the CloudFront cache.

### Triggering the Workflow

This workflow is triggered manually using `workflow_dispatch`.

> [!IMPORTANT]
> Ensure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are in Github environment secrets and are valid.

1.  Navigate to the **Actions** tab in your GitHub repository.
2.  In the left sidebar, under **Workflows**, click on **[PRODUCTION Deploy](https://github.com/ustaxcourt/website-wagtail/actions/workflows/production_deploy.yml)**.
3.  On the right side of the page, click the **Run workflow** button.
4.  A modal window will appear prompting you to provide input:
    * **Use workflow from: ** Select `production` branch (change default from `main`).
    * **commit\_sha (string, required):** Enter the specific commit SHA (the unique identifier of a commit) that you want to deploy to production. Ensure this is the correct and tested commit.
5.  Click the green **Run workflow** button at the bottom of the modal.
6.  Wait for the workflow to complete successfully.
7.  Validate the website version by checking the `Build: <sha>` in the website footer.
8.  Remove any production environment secrets in Github environment setting.

### Workflow Steps

The workflow consists of the following jobs and steps:

**Job: `production-deploy`**

* **Environment:** `production` - This designates that the job runs in the `production` environment, which can be configured with specific secrets and settings in your repository settings.
* **Runs On:** `ubuntu-latest` - Specifies that the job will run on the latest version of the Ubuntu Linux runner provided by GitHub Actions.
* **Timeout Minutes:** `45` - Sets a maximum execution time of 45 minutes for the entire job. If the job exceeds this limit, it will be automatically cancelled.

**Steps:**

1.  **Check deployer permission:**
    * **Environment Variables:**
        * `ACTOR`: The GitHub username of the user who triggered the workflow (`${{ github.actor }}`).
        * `APPROVED`: A comma-separated list of authorized GitHub usernames stored as a repository variable named `APPROVED_DEPLOYERS` (`${{ vars.APPROVED_DEPLOYERS }}`).
    * **Functionality:** This step verifies if the user who initiated the workflow is authorized to deploy to production. It retrieves the list of approved deployers from the `APPROVED_DEPLOYERS` repository variable and checks if the `github.actor` matches any of the users in the list.
    * **Outcome:** If the user is authorized, the step exits with a success code (0). If the user is not authorized, the step exits with an error code (1), and the workflow will fail.
    * **Troubleshooting:** If you are unable to trigger the deployment, ensure your GitHub username is included in the `APPROVED_DEPLOYERS` repository variable. This variable can be managed in your repository settings under "Variables".

2.  **Set Environment:**
    * **ID:** `set_env`
    * **Functionality:** This step sets an environment variable named `ENVIRONMENT` with the value `production`. This variable can be used by subsequent steps to conditionally execute commands or configure tools for the production environment.

3.  **Checkout specific commit:**
    * **Uses:** `actions/checkout@v3` - This action checks out your repository code onto the runner.
    * **With:**
        * `ref`: `${{ github.event.inputs.commit_sha }}` - Specifies the exact commit SHA provided during the workflow trigger that should be checked out. This ensures that the deployment is based on the intended version of the code.

4.  **Set up Terraform:**
    * **Uses:** `./.github/actions/setup-terraform` - Sets up terraform version to the version mentioned in [.terraform-version](../../.terraform-version) file.

5.  **Set up Python:**
    * **Uses:** `./.github/actions/setup-python` - Sets up python version to the version mentioned in [.python-version](../../website/.python-version) file.

6.  **Setup Node:**
    * **Uses:** `./.github/actions/setup-node` - Sets up node version.

7.  **Build USWDS:**
    * **Functionality:** Builds USWDS assets needed for website.

8.  **Apply Terraform:**
    * **Environment Variables:**
        * `AWS_ACCESS_KEY_ID`: Your AWS access key ID, stored as a GitHub secret (`${{ secrets.AWS_ACCESS_KEY_ID }}`).
        * `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key, stored as a GitHub secret (`${{ secrets.AWS_SECRET_ACCESS_KEY }}`). **Ensure these secrets are properly configured in your repository settings.**
    * **Functionality:**
        * Deploys infrastructure changes using AWS credentials from secrets. Outputs bastion IP, database endpoint, and bucket name.

9.  **Set up SSH Key:**
    * Enables Github action runners to connect to Bastion HOST and RDS from there.

10. **Perform Production Checks:**
    * **Functionality:**
        * Runs checks against the deployed environment via an SSH tunnel to the database through the bastion host.

11. **Run Migrations:**
    * **Functionality:**
        * Applies database migrations and creates a superuser (if needed) via the SSH tunnel.

12. **Deploy ECS Task (Post-Migration):**
    * **Functionality:**
        * Updates the production ECS service with the new task definition.
