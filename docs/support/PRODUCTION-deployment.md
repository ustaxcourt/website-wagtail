## Support Documentation: PRODUCTION Deploy Workflow

This document provides guidance on how to use the `PRODUCTION Deploy` GitHub workflow to deploy code changes to the production environment.

### Purpose

The `PRODUCTION Deploy` workflow automates the process of deploying a specific commit to the production environment. It sets up the necessary environment, interfaces with Github using Open ID connect (OIDC) and deploys infrastructure changes using Terraform, runs database migrations, updates the ECS service, and invalidates the CloudFront cache.

### Triggering the Workflow

This workflow is triggered manually using `workflow_dispatch`.

#### AWS Role Permission Changes

> [!IMPORTANT]
> Ensure the IAM role: "github-workflow-deployer" has permissions/policy: "deployer-policy".

1. Navigate to the IAM service in the AWS Management Console.
2. In the left navigation pane, click on Roles.
3. Find and click on the role named github-workflow-deployer.
4. In the Permissions tab, click the Add permissions dropdown and select Attach policies.
5. In the search box, type deployer-policy to find the powerful managed policy.
6. Select the checkbox next to deployer-policy and click the Attach policies button.

#### Starting Github Workflow

1.  Navigate to the **Actions** tab in the GitHub repository.
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

1.  **Configure AWS credentials from Prod account**
* Functionality: This step uses OIDC to exchange a token from GitHub for temporary AWS credentials. Crucially, it assumes the `github-workflow-deployer` role in its default state, which has no deployment permissions. It can only check its own policies and later detach them.

* Verify AWS Deployer Role (Poll for Policy Attachment): This is the waiting gate. It runs a while true loop that uses the AWS CLI to repeatedly call `iam:list-attached-role-policies` on its own role. It will only break the loop and allow the workflow to continue when it detects that the deployer-policy has been attached by an AWS Administrator.

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
