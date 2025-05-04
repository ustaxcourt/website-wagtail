# Workflow Documentation: Manual RDS Restore from Snapshot

## Overview

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

**Note:** Additional sensitive information like `DATABASE_PASSWORD`, `DJANGO_SUPERUSER_PASSWORD`, `SECRET_KEY`, `DATABASE_HOSTNAME`, `BASTION_HOST_IP`, and `BASTION_PRIVATE_KEY` are expected to be fetched dynamically during the workflow execution by the `infra/load-secrets.sh` script, likely from AWS Secrets Manager or Parameter Store based on the selected `environment`.

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
* **Commands:** `cd infra`, `source ./setup.sh`, `source ./setup_zone.sh`, `./update-deployer-policy.sh`, `terraform init ...`, `terraform refresh`, `terraform apply -target=module.app.aws_security_group.bastion_sg ...`
* **Description:** This crucial step prepares for SSH access. It navigates to the `infra` directory, configures Terraform backend using environment-specific settings (via `setup.sh`, `setup_zone.sh`), potentially updates an IAM policy (`update-deployer-policy.sh`), initializes Terraform, refreshes state, and then applies a targeted change ONLY to the bastion host's security group (`module.app.aws_security_group.bastion_sg`). This modification likely adds a rule to allow SSH traffic from the GitHub Actions runner's current IP address.
* **Inputs/Environment:** AWS Credentials, `$ENVIRONMENT`, Terraform state in S3/DynamoDB, local Terraform code (`infra/`), scripts (`setup.sh`, `setup_zone.sh`, `update-deployer-policy.sh`).
* **Expected Outcome:** The bastion host's security group (`aws_security_group.bastion_sg` within `module.app`) is updated to allow SSH connections from the runner.
* **Potential Errors & Troubleshooting:**
    * *Error:* Script failures (`setup.sh`, `setup_zone.sh`, `update-deployer-policy.sh`).
        * *Troubleshooting:* Check the logic and execution permissions of these scripts. Ensure they correctly source variables based on `$ENVIRONMENT`.
    * *Error:* Terraform initialization failure (backend configuration errors, unable to access S3 bucket or DynamoDB table).
        * *Troubleshooting:* Verify bucket/table names and regions. Check IAM permissions for accessing the Terraform backend state.
    * *Error:* Terraform refresh/apply failure (state lock, invalid Terraform code, AWS API errors, insufficient IAM permissions for `ec2:AuthorizeSecurityGroupIngress`/`ec2:DescribeSecurityGroups`, etc.).
        * *Troubleshooting:* Check Terraform logs for details. Release state lock if necessary. Validate Terraform code (`terraform validate`). Ensure AWS credentials have permissions to modify the target security group.
    * *Error:* Target `module.app.aws_security_group.bastion_sg` not found in Terraform state.
        * *Troubleshooting:* Verify the Terraform module structure and resource naming is correct.

---

**8. Load Secrets and Set up SSH Key**
* **Commands:** `cd infra`, `. ./load-secrets.sh`, `cd ..`, export secrets to `$GITHUB_ENV`, decode and save SSH key.
* **Description:** Executes the `infra/load-secrets.sh` script, which is expected to fetch sensitive data (DB credentials, hostnames, bastion SSH private key) from AWS Secrets Manager or Parameter Store based on `$ENVIRONMENT`. It then exports these fetched values as masked environment variables for subsequent steps and decodes the base64 encoded bastion private key, saving it to `~/.ssh/id_rsa` with appropriate permissions (600).
* **Inputs/Environment:** AWS Credentials, `$ENVIRONMENT`, script `infra/load-secrets.sh`. Assumes secrets exist in AWS.
* **Expected Outcome:** Secrets like `$DATABASE_PASSWORD`, `$DATABASE_HOSTNAME`, `$BASTION_HOST_IP`, `$BASTION_PRIVATE_KEY` etc. are fetched and available as environment variables. The SSH private key file `~/.ssh/id_rsa` is created and configured.
* **Potential Errors & Troubleshooting:**
    * *Error:* `load-secrets.sh` script fails (e.g., cannot connect to AWS, secret not found in Secrets Manager/Parameter Store, permission denied).
        * *Troubleshooting:* Check the script's logic and logs. Verify the secrets exist in the expected AWS location for the given `$ENVIRONMENT`. Ensure AWS credentials have permissions (`secretsmanager:GetSecretValue` or `ssm:GetParameter`).
    * *Error:* Base64 decoding fails (invalid `BASTION_PRIVATE_KEY` format).
        * *Troubleshooting:* Ensure the secret stored in AWS is a valid base64 encoded private key.
    * *Error:* Filesystem errors creating `~/.ssh` directory or writing `id_rsa` file.
        * *Troubleshooting:* Check runner filesystem permissions (usually not an issue on standard runners).

---

**9. Run RDS Restore Script (Conditional)**
* **Condition:** `if: github.event.inputs.create_backup_db == 'Yes'`
* **Command:** `./infra/restore-rds.sh "${{ github.event.inputs.source_instance_id }}" "${{ github.event.inputs.snapshot_id }}"`
* **Description:** If the user selected 'Yes' for `create_backup_db`, this step executes the main RDS restore script (`./infra/restore-rds.sh`), passing the source instance ID and target snapshot ID as arguments. The script contains the core logic for interacting with the AWS RDS API to perform the restore operation (likely `aws rds restore-db-instance-from-db-snapshot`). **The exact behavior (e.g., creating a *new* instance vs. restoring over an existing one) depends entirely on the content of `restore-rds.sh`.**
* **Inputs/Environment:** AWS Credentials, `github.event.inputs.source_instance_id`, `github.event.inputs.snapshot_id`, depends on the implementation within `restore-rds.sh`.
* **Expected Outcome:** An RDS instance is restored from the specified snapshot. This is often a long-running operation; the script might wait for completion or exit earlier.
* **Potential Errors & Troubleshooting:**
    * *Error:* Script `./infra/restore-rds.sh` not found or not executable.
        * *Troubleshooting:* Ensure the script exists, is checked into the repository, and has execute permissions (`chmod +x`).
    * *Error:* AWS API errors during restore (snapshot not found, invalid source instance ID, instance identifier already exists, insufficient IAM permissions `rds:RestoreDBInstanceFromDBSnapshot`, RDS limits exceeded, incompatible parameters).
        * *Troubleshooting:* Check the script's output for AWS error messages. Verify snapshot ID and source instance ID. Ensure the IAM user/role has RDS restore permissions. Check RDS console for conflicting instance names or resource limits.
    * *Error:* Script timeout if it waits for instance availability, which can take a long time.
        * *Troubleshooting:* Increase timeout settings if necessary, or modify the script to not wait.

---

**10. Run Migrations (Conditional)**
* **Condition:** `if: github.event.inputs.apply_migration == 'Yes'`
* **Commands:** `cd website`, `ssh-keyscan`, `ssh -L ...` (tunnel), `export DATABASE_URL`, `make migrate`, `make createpages`
* **Description:** If the user selected 'Yes' for `apply_migration`, this step performs database migrations:
    1.  Changes to the `website` directory.
    2.  Adds the bastion host's SSH key to the runner's `known_hosts` file using `ssh-keyscan`.
    3.  Establishes an SSH tunnel in the background (`-f -N`). It forwards connections from the runner's `localhost:5432` to the actual database host (`$DATABASE_HOSTNAME:5432`) via the bastion host (`$BASTION_HOST_IP`), using the SSH key set up earlier.
    4.  Exports a `DATABASE_URL` environment variable pointing to `localhost:5432` using the fetched `$DATABASE_PASSWORD`.
    5.  Runs `make migrate` (presumably executing `python manage.py migrate`) to apply Django database migrations using the tunnelled connection.
    6.  Runs `make createpages settings="app.settings.${ENVIRONMENT}"`, a custom command likely performing post-migration data setup specific to the environment.
* **Inputs/Environment:** `$BASTION_HOST_IP`, `$DATABASE_HOSTNAME`, `$DATABASE_PASSWORD`, `$ENVIRONMENT`, SSH key (`~/.ssh/id_rsa`), Python environment with dependencies, `website/Makefile`, `manage.py` script. Requires the bastion security group update (Step 7) to have succeeded. Requires the RDS instance (either pre-existing or restored in Step 9) to be available and accessible from the bastion.
* **Expected Outcome:** Database schema migrations are applied, and any custom post-migration setup (`createpages`) is executed successfully.
* **Potential Errors & Troubleshooting:**
    * *Error:* `ssh-keyscan` fails (bastion host unreachable, DNS resolution issues).
        * *Troubleshooting:* Verify `$BASTION_HOST_IP` is correct and reachable from the runner. Check network ACLs and Security Groups on the bastion.
    * *Error:* SSH tunnel command fails (`ssh -L ...`):
        * *Permission denied:* SSH key issue (`~/.ssh/id_rsa` incorrect, permissions wrong, key not authorized on bastion). Troubleshooting: Verify key generation/loading (Step 8). Check bastion's `~/.ssh/authorized_keys`.
        * *Connection refused/timeout:* Bastion host down, port 22 blocked (check bastion SG, network ACLs), incorrect `$BASTION_HOST_IP`. Troubleshooting: Verify bastion status and network paths. Ensure Step 7 successfully allowed runner IP.
        * *Host key verification failed:* Issue with `known_hosts` file or host key changing. `StrictHostKeyChecking=yes` requires the key scanned by `ssh-keyscan` to be correct. Troubleshooting: Ensure `ssh-keyscan` ran correctly. Clear `~/.ssh/known_hosts` if the key legitimately changed (use caution).
        * *Address already in use:* Port 5432 on the runner is already bound. Troubleshooting: Unlikely in clean runner environment, but check for conflicting processes if debugging locally.
    * *Error:* `make migrate` or `make createpages` fails:
        * *Database connection error:* Tunnel not working, `$DATABASE_HOSTNAME` incorrect, database instance not running or accessible from bastion, incorrect `$DATABASE_PASSWORD`, wrong database name in `DATABASE_URL`. Troubleshooting: Verify tunnel status (`ps aux | grep ssh`). Check database status in AWS console. Ensure bastion's outbound rules allow connection to DB port. Verify credentials.
        * *Migration script errors:* Syntax errors in Django migrations, logical errors in migration code, data conflicts. Troubleshooting: Examine Django migration logs. Test migrations locally or in a staging environment.
        * *`createpages` command errors:* Issues specific to the custom logic in that command. Troubleshooting: Check the `make createpages` target in the Makefile and the corresponding Python script/management command.

---

## Important Considerations

* **Security:** This workflow uses static AWS Access Keys stored as GitHub secrets. Consider migrating to OpenID Connect (OIDC) using `aws-actions/configure-aws-credentials` with `role-to-assume` for enhanced security (eliminates long-lived keys).
* **Idempotency:** The `restore-rds.sh` script's behavior is critical. If it creates a *new* instance, running the workflow multiple times might create multiple restored instances. If it modifies an existing instance, it might be destructive. Ensure the script's behavior is well-understood.
* **State Management:** Terraform is used for a targeted SG update. Ensure the Terraform state is managed correctly (S3 backend with locking is good practice, as used here).
* **External Scripts:** The workflow heavily relies on the correctness and robustness of external scripts (`restore-rds.sh`, `load-secrets.sh`, `setup.sh`, `setup_zone.sh`, Makefiles). Errors within these scripts will cause workflow failures.
* **Long-Running Operations:** RDS restore can take significant time. The workflow might time out if scripts wait synchronously without adequate timeout settings.
* **Bastion Dependency:** Access to the database for migrations relies entirely on the bastion host being available and correctly configured, and the runner's IP being allowed through its security group.
* **Dynamic Sandbox Environment:** Note that the GitHub Actions environment name for `sandbox` includes the triggering actor's username (`{github.actor}_sandbox`), making it specific to the user running the workflow.
