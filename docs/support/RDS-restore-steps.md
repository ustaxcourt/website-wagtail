# Workflow Documentation: Manual RDS Restore from Snapshot

## Local Execution Overview

It's possible to perform the core actions of the Database restore workflow (restore, tunnel, migrate) from your local machine using `make` commands. This is useful optional manual action to performing restores outside of GitHub Actions.

> [!WARNING]
> The local execution process and the GitHub Actions workflow have diverged. The GitHub workflow now includes more dynamic steps (like fetching the DB hostname automatically) and no longer runs `make createpages`.

### Prerequisites

- **AWS Credentials:** Configure AWS credentials locally with sufficient permissions for RDS restore, EC2 Security Group modifications, and potentially accessing secrets (e.g., via `aws configure`, or setting `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` environment variables).
- **DATABASE_HOSTNAME:** Configure `DATABASE_HOSTNAME` in AWS Secrets manager for secret: `website_secrets`. This should be the restored Database hostname.
- **BASTION_HOST_IP:** Configure `BASTION_HOST_IP` in AWS Secrets manager for secret: `website_secrets`.

**Steps:**

The process typically involves three main `make` commands run in sequence:

**1. Create DB Restore:**

* **Purpose:** Initiates the AWS RDS restore process, creating a new instance from the specified snapshot. Corresponds to the "Run RDS Restore Script" step in the GitHub workflow.
* **Command Syntax:**
    ```bash
    make create-db-restore db_instance_id=<source_instance_id> db_snapshot_id=<snapshot_id>
    ```
* **Example:**
    ```bash
    make create-db-restore db_instance_id=sandbox-20250503200625381200000001 db_snapshot_id=rds:sandbox-20250503200625381200000001-2025-05-03-20-10
    ```
* **Action:** Executes the `infra/restore-rds.sh` script, passing the instance and snapshot IDs. This is an AWS operation and may take considerable time for the new RDS instance to become available.

**2. Start SSH Tunnel:**

> [!IMPORTANT]
> Check that you have correctly configured `BASTION_HOST_IP` in `website_secrets`.

* **Purpose:** Prepares for database connection by:
    * Updating the bastion host's security group via Terraform to allow SSH from your *current* public IP.
    * Fetching necessary secrets (like bastion key, DB hostname - likely handled within the script).
    * Setting up the bastion's private key locally (`./infra/.ssh/id_rsa`).
    * Adding the bastion's host key to `./infra/.ssh/known_hosts`.
    * Starting the SSH tunnel process **in the background**.
    Corresponds to the "Update Bastion SG", "Load Secrets/Set up SSH Key", and SSH tunnel setup parts of the GitHub workflow.
* **Command:**
    ```bash
    make start-tunnel
    ```
* **Action:** Executes the `infra/ssh-tunnel.sh` script.
* **Outcome:** This command will print status messages and typically exit quickly after launching the SSH tunnel process in the background (using `ssh -f`). The tunnel forwarding `localhost:5432` to the database will remain active in the background.

**3. Apply Migrations to Restored DB:**

> [!IMPORTANT]
> Check that you have correctly configured `DATABASE_HOSTNAME` in `website_secrets`.

* **Purpose:** Connects to the newly restored database (via the background tunnel established in Step 2) and applies database migrations.
* **Command:**
    ```bash
    make apply-db-restore
    ```
* **Action:** Executes the `infra/apply-migrations-to-restored-db.sh` script. This script likely sets the `DATABASE_URL` environment variable to point to `localhost:5432` and then runs the necessary `make migrate` command.
* **Prerequisite:** Requires the SSH tunnel from `make start-tunnel` to be running in the background.

**Important Notes for Local Execution:**

* **Environment:** Environment is inferred from the AWS session key.
* **Tunnel Management:** The `make start-tunnel` command starts the tunnel in the background. You will need to manage this process separately if you need to stop it (e.g., using `ps aux | grep ssh` to find the process ID and `kill <PID>`).
* **Security Group Cleanup:** The `infra/ssh-tunnel.sh` script (as invoked by `make start-tunnel`) modifies the bastion security group to allow your IP.
* **Error Handling:** Pay close attention to the output of each command for any errors during execution.

## Github Action Overview

This GitHub Actions workflow provides a manual mechanism to restore an AWS Relational Database Service (RDS) instance from a specified snapshot. It is designed to be triggered manually via the GitHub Actions UI (`workflow_dispatch`). The workflow handles AWS authentication, infrastructure updates (specifically bastion host access), the core RDS restore operation (conditionally), and database migrations (conditionally) via an SSH tunnel through a bastion host.

**Purpose:** To enable controlled database restores for environments like sandbox, development, or production from known snapshots, potentially followed by database schema migrations.

**Technology Stack:**
* GitHub Actions
* AWS CLI / SDK (implicitly via `aws-actions/configure-aws-credentials` and scripts)
* Terraform (for infrastructure adjustments)
* Python/Django (for database migrations via `make`)
* Bash (for orchestration scripts like `restore-rds.sh`, `load-secrets.sh`)
* SSH (for tunneling to the database via bastion)

## Trigger

* **Type:** Manual (`workflow_dispatch`)
* **How to trigger:** Navigate to the Actions tab in the GitHub repository, select "Manual RDS Restore from Snapshot" from the workflow list, and click "Run workflow". You will be prompted to provide the necessary inputs.

## Inputs

The workflow requires the following inputs when triggered manually:

| Parameter            | Description                                 | Type    | Required | Options                    | Default   |
| :------------------- | :------------------------------------------ | :------ | :------- | :------------------------- | :-------- |
| `environment`        | Target AWS environment for the restore.     | `choice`  | Yes      | `sandbox`, `dev`, `production` | `sandbox` |
| `source_instance_id` | The identifier of the original RDS instance from which the snapshot was taken. | `string`  | Yes      | N/A                        | N/A       |
| `snapshot_id`        | The specific RDS snapshot identifier to restore from. | `string`  | Yes      | N/A                        | N/A       |
| `create_backup_db`   | Choose 'Yes' to execute the RDS restore script. Select 'No' to skip the actual restore step (e.g., only run migrations on an existing DB). | `choice`  | No       | `No`, `Yes`                | `Yes`     |
| `apply_migration`    | Choose 'Yes' to apply database migrations after the restore (if performed). Select 'No' to skip migrations. | `choice`  | No       | `No`, `Yes`                | `No`      |

## Required Secrets

The workflow relies on the following GitHub Actions secrets:

| Secret Name             | Description                                                                 | Scope       |
| :---------------------- | :-------------------------------------------------------------------------- | :---------- |
| `AWS_ACCESS_KEY_ID`     | AWS Access Key ID for authentication. Must have sufficient IAM permissions. | Environment |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key associated with the Access Key ID.                    | Environment |

**Note:** Additional sensitive information like `DATABASE_PASSWORD`, `DJANGO_SUPERUSER_PASSWORD`, `SECRET_KEY`, and `BASTION_PRIVATE_KEY` are expected to be fetched dynamically during the workflow execution by the `infra/load-secrets.sh` script. Other variables like the DB hostname and bastion IP are determined dynamically within the workflow.

## Workflow Environment Configuration

The workflow dynamically sets the GitHub Actions `environment` based on the `environment` input:

* If input `environment` is `sandbox`, the GitHub environment `{triggering_actor}_sandbox` is used (e.g., `username_sandbox`).

This allows for environment-specific secrets and protection rules within GitHub.

## Workflow Steps

Here's a breakdown of each step in the `rds-restore` job:

---

**1. Checkout code**
* **Action:** `actions/checkout@v4`
* **Description:** Checks out the repository code onto the GitHub Actions runner, making local scripts and configuration available.
* **Inputs/Environment:** None.
* **Expected Outcome:** Repository code is present in the runner's workspace.
* **Potential Errors & Troubleshooting:**
    * *Error:* Network issues cloning the repository.
        * *Troubleshooting:* Retry the workflow. Check GitHub status.
    * *Error:* Insufficient permissions to access the repository (if it's private and runner doesn't have access).
        * *Troubleshooting:* Ensure the Action has `contents: read` permission (as configured). Check repository access settings.

---

**2. Set Environment Variable**
* **Command:** `echo "ENVIRONMENT=${{ github.event.inputs.environment }}" >> $GITHUB_ENV`
* **Description:** Sets an environment variable `ENVIRONMENT` within the runner based on the user's `environment` input. This is used by subsequent scripts (e.g., `setup.sh`, `load-secrets.sh`).
* **Inputs/Environment:** `github.event.inputs.environment`.
* **Expected Outcome:** The `$ENVIRONMENT` variable is available for later steps.
* **Potential Errors & Troubleshooting:**
    * *Error:* Unlikely, unless there's a fundamental issue with the runner environment or `$GITHUB_ENV` file.
        * *Troubleshooting:* Verify runner health. Check workflow syntax.

---

**3. Configure AWS Credentials**
* **Action:** `aws-actions/configure-aws-credentials@v4`
* **Description:** Configures AWS credentials using the provided GitHub secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) for the `us-east-1` region. Allows subsequent steps to interact with AWS services.
* **Inputs/Environment:** `secrets.AWS_ACCESS_KEY_ID`, `secrets.AWS_SECRET_ACCESS_KEY`.
* **Expected Outcome:** AWS CLI and SDKs are configured with valid credentials.
* **Potential Errors & Troubleshooting:**
    * *Error:* Invalid credentials (wrong keys, expired keys).
        * *Troubleshooting:* Verify the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets are correct and active in the GitHub environment settings.
    * *Error:* IAM user/role associated with the keys lacks necessary permissions for subsequent AWS actions (RDS, EC2 SG updates, Secrets Manager/Parameter Store access).
        * *Troubleshooting:* Review and update the IAM policy attached to the credentials to include required permissions (e.g., `rds:RestoreDBInstanceFromDBSnapshot`, `ec2:AuthorizeSecurityGroupIngress`, `ec2:RevokeSecurityGroupIngress`, `secretsmanager:GetSecretValue`, etc.).

---

**4. Set up Terraform**
* **Action:** `./.github/actions/setup-terraform` (Local composite action)
* **Description:** Executes a local composite action to set up the Terraform environment on the runner. The exact steps are defined within that action's definition file (`./.github/actions/setup-terraform/action.yml`). Typically involves installing Terraform CLI.
* **Inputs/Environment:** None directly to this step, but subsequent Terraform steps depend on AWS credentials and `$ENVIRONMENT`.
* **Expected Outcome:** Terraform CLI is installed and ready for use.
* **Potential Errors & Troubleshooting:**
    * *Error:* Composite action file not found or has syntax errors.
        * *Troubleshooting:* Verify the path `./.github/actions/setup-terraform` is correct and the `action.yml` file exists and is valid.
    * *Error:* Failures during Terraform installation (e.g., network issues downloading).
        * *Troubleshooting:* Check the composite action's script logs. Retry the workflow.

---

**5. Set up Python**
* **Action:** `./.github/actions/setup-python` (Local composite action)
* **Description:** Executes a local composite action to set up the Python environment. Likely involves installing a specific Python version.
* **Inputs/Environment:** None directly.
* **Expected Outcome:** Python interpreter is available.
* **Potential Errors & Troubleshooting:**
    * *Error:* Composite action file not found or has syntax errors.
        * *Troubleshooting:* Verify path and `action.yml` validity.
    * *Error:* Failures during Python setup (network issues, incompatible runner OS).
        * *Troubleshooting:* Check the composite action's script logs.

---

**6. Setup Python Dependencies**
* **Commands:** `cd website`, `make setup`
* **Description:** Changes into the `website` directory and runs `make setup`. This command is expected to install Python packages required for the Django application, typically using `pip` and a `requirements.txt` file defined within the Makefile target.
* **Inputs/Environment:** Requires Python to be set up. Depends on the contents of `website/Makefile`.
* **Expected Outcome:** All Python dependencies listed in `website/requirements.txt` (or equivalent) are installed.
* **Potential Errors & Troubleshooting:**
    * *Error:* `website` directory not found.
        * *Troubleshooting:* Ensure `actions/checkout` ran successfully and the directory structure is correct.
    * *Error:* `make` command not found.
        * *Troubleshooting:* Ensure `make` is installed on the `ubuntu-latest` runner (it usually is) or add an installation step.
    * *Error:* `make setup` target fails (e.g., `pip install` errors due to network issues, package conflicts, missing system libraries).
        * *Troubleshooting:* Check the output logs for specific `pip` errors. Update `requirements.txt` or the runner environment if system dependencies are missing. Examine the `website/Makefile`.

---

**7. Update Bastion SG for Runner Access**
* **Condition:** `if: github.event.inputs.apply_migration == 'Yes'`
* **Commands:** `cd infra`, `source ./setup.sh`, `...`, `terraform apply ...`
* **Description:** This crucial step prepares for SSH access. It navigates to the `infra` directory, configures and initializes Terraform, and then applies a targeted change to the bastion host's security group and instance. This modification allows SSH traffic from the GitHub Actions runner's IP address. It concludes by outputting the bastion's public IP (`bastion_public_ip`) for use in later steps.
* **Inputs/Environment:** AWS Credentials, `$ENVIRONMENT`, Terraform state in S3/DynamoDB.
* **Expected Outcome:** The bastion host's security group is updated to allow SSH from the runner, and its public IP is available as a step output.
* **Potential Errors & Troubleshooting:**
    * *Error:* Script failures (`setup.sh`, etc.).
        * *Troubleshooting:* Check the logic and execution permissions of these scripts.
    * *Error:* Terraform initialization or apply failure (backend access, state lock, invalid code, AWS API errors, insufficient IAM permissions).
        * *Troubleshooting:* Check Terraform logs. Ensure AWS credentials have permissions to modify the target resources.
    * *Error:* Target resource not found in Terraform state.
        * *Troubleshooting:* Verify the Terraform module structure and resource naming is correct.

---

**8. Load Secrets and Set up SSH Key**
* **Commands:** `cd infra`, `. ./load-secrets.sh`, `cd ..`, decode and save SSH key.
* **Description:** Executes the `infra/load-secrets.sh` script to fetch sensitive data (DB password, Django secret key, bastion SSH private key) from AWS Secrets Manager. It then exports these fetched values as masked environment variables and decodes the base64 encoded bastion private key, saving it to `~/.ssh/id_rsa` with appropriate permissions (600).
* **Inputs/Environment:** AWS Credentials, `$ENVIRONMENT`, script `infra/load-secrets.sh`.
* **Expected Outcome:** Secrets like `$DATABASE_PASSWORD` and `$BASTION_PRIVATE_KEY` are fetched and available. The SSH private key file `~/.ssh/id_rsa` is created and configured.
* **Potential Errors & Troubleshooting:**
    * *Error:* `load-secrets.sh` script fails (secret not found, permission denied).
        * *Troubleshooting:* Check the script's logic. Verify the secrets exist in AWS Secrets Manager for the given `$ENVIRONMENT`. Ensure AWS credentials have `secretsmanager:GetSecretValue` permission.
    * *Error:* Base64 decoding fails (invalid `BASTION_PRIVATE_KEY` format).
        * *Troubleshooting:* Ensure the secret stored in AWS is a valid base64 encoded private key.

---

**9. Run RDS Restore Script (Conditional)**
* **Condition:** `if: github.event.inputs.create_backup_db == 'Yes'`
* **Command:** `./infra/restore-rds.sh "${{ github.event.inputs.source_instance_id }}" "${{ github.event.inputs.snapshot_id }}"`
* **Description:** If the user selected 'Yes' for `create_backup_db`, this step executes the main RDS restore script (`./infra/restore-rds.sh`). The script uses the AWS CLI to restore a new DB instance from the specified snapshot, using the configuration of the source instance. The script waits for the new instance to become available.
* **Inputs/Environment:** AWS Credentials, `github.event.inputs.source_instance_id`, `github.event.inputs.snapshot_id`.
* **Expected Outcome:** A new RDS instance named `{source_instance_id}-restored` is created and available.
* **Potential Errors & Troubleshooting:**
    * *Error:* Script `./infra/restore-rds.sh` not found or not executable.
        * *Troubleshooting:* Ensure the script exists and has execute permissions (`chmod +x`).
    * *Error:* AWS API errors during restore (snapshot not found, instance identifier already exists, insufficient IAM permissions `rds:RestoreDBInstanceFromDBSnapshot`).
        * *Troubleshooting:* Check the script's output for AWS error messages. Verify inputs. Ensure the target instance name doesn't already exist.
    * *Error:* Script timeout if it waits for instance availability, which can take a long time.
        * *Troubleshooting:* The job timeout in GitHub Actions might be reached.

---

**10. Run Migrations (Conditional)**
* **Condition:** `if: github.event.inputs.apply_migration == 'Yes'`
* **Commands:** `cd website`, determine `DATABASE_HOSTNAME`, `ssh-keyscan`, `ssh -L ...` (tunnel), `export DATABASE_URL`, `make migrate`
* **Description:** If the user selected 'Yes' for `apply_migration`, this step performs database migrations:
    1.  **Dynamically determines the new database endpoint address.** It calls `aws rds describe-db-instances` for the newly created instance (`{source_instance_id}-restored`) and extracts its endpoint address.
    2.  Adds the bastion host's SSH key to the runner's `known_hosts` file using `ssh-keyscan`.
    3.  Establishes an SSH tunnel in the background (`-f -N`). It forwards connections from the runner's `localhost:5432` to the dynamically discovered database host (`$DATABASE_HOSTNAME:5432`) via the bastion host (`$BASTION_HOST_IP`), using the SSH key set up earlier.
    4.  Exports a `DATABASE_URL` environment variable pointing to `localhost:5432` using the fetched `$DATABASE_PASSWORD`.
    5.  Runs `make migrate` (presumably executing `python manage.py migrate`) to apply Django database migrations using the tunnelled connection.
* **Inputs/Environment:** `$BASTION_HOST_IP` (from step 7 output), `$DATABASE_PASSWORD`, `$ENVIRONMENT`, SSH key (`~/.ssh/id_rsa`), Python environment with dependencies.
* **Expected Outcome:** Database schema migrations are applied successfully to the newly restored database.
* **Potential Errors & Troubleshooting:**
    * *Error:* Failed to describe RDS instance to get hostname (instance not found, permissions issue).
        * *Troubleshooting:* Ensure the restore step completed successfully and the instance name is correct. Check IAM permissions for `rds:DescribeDBInstances`.
    * *Error:* `ssh-keyscan` fails (bastion host unreachable).
        * *Troubleshooting:* Verify `$BASTION_HOST_IP` is correct and reachable. Check network ACLs and Security Groups on the bastion.
    * *Error:* SSH tunnel command fails (`ssh -L ...`):
        * *Permission denied:* SSH key issue or key not authorized on bastion.
        * *Connection refused/timeout:* Bastion host down, port 22 blocked, or incorrect `$BASTION_HOST_IP`. Ensure Step 7 successfully allowed the runner's IP.
    * *Error:* `make migrate` fails:
        * *Database connection error:* Tunnel not working, dynamically discovered `$DATABASE_HOSTNAME` is incorrect, DB not accessible from bastion, or incorrect credentials.
        * *Migration script errors:* Syntax or logical errors in Django migrations.

---

## Important Considerations

* **Security:** This workflow uses static AWS Access Keys stored as GitHub secrets. Consider migrating to OpenID Connect (OIDC) using `aws-actions/configure-aws-credentials` with `role-to-assume` for enhanced security (eliminates long-lived keys).
* **Idempotency:** The `restore-rds.sh` script creates a new instance with a predictable name (`{source_instance_id}-restored`). Running the workflow multiple times with the same `source_instance_id` will fail on the second run because the target DB instance will already exist.
* **State Management:** Terraform is used for a targeted SG update. Ensure the Terraform state is managed correctly (S3 backend with locking is good practice, as used here).
* **External Scripts:** The workflow heavily relies on the correctness and robustness of external scripts (`restore-rds.sh`, `load-secrets.sh`, `setup.sh`, etc.) and Makefiles.
* **Long-Running Operations:** RDS restore can take significant time. The workflow might time out if scripts wait synchronously without adequate timeout settings.
* **Bastion Dependency:** Access to the database for migrations relies entirely on the bastion host being available and correctly configured, and the runner's IP being allowed through its security group.
* **Dynamic Sandbox Environment:** Note that the GitHub Actions environment name for `sandbox` includes the triggering actor's username (`{github.actor}_sandbox`), making it specific to the user running the workflow.
