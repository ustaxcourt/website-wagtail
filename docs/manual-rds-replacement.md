# Manual RDS Database Replacement Procedure

## Overview

This document describes the steps to manually replace the Wagtail website’s RDS database with a restored snapshot using the AWS Console.

---

## Steps

### 1. Create a Snapshot of the Current Database

- Go to **AWS Console > RDS > Databases**.
- Select the active database.
- Click **Actions > Take snapshot**.
- Name the snapshot (e.g., `pre-replacement-snapshot`).
- Confirm (Take snapshot) and wait for the snapshot to complete.

### 2. Restore Database from Snapshot

- Go to **RDS > Snapshots**.
- Select the desired snapshot.
- Click **Actions > Restore snapshot** to create a new RDS instance.
- Configure instance details (you get the values from your existing DB instance to ensure your restored snapshot has the same configuration.)
    - RDS Console → Databases → click your DB → Configuration tab
        - DB instance settings → DB engine
        - Availability and durability → Deployment options
        - Settings → DB instance identifier - shows current DB instance ID (Enter a uniq ID)
        - Instance configuration → DB instance class
        - Storage → Storage type
        - Storage → Allocated storage
        - Connectivity → Availability Zone
        - Certificate authority (optional)
        - Database authentication → Database authentication options
        - Additional configuration (Database options, Backup, IAM role, Maintenance.)

    - Under Connectivity & Security tab
        - Connectivity → Virtual private cloud (VPC)
        - Connectivity → DB subnet group
        - Connectivity → Public access
        - Connectivity → Existing VPC security groups

    - Under Tags tab
        - Tags – optional

- Launch the instance and wait for it to become available.

### 3. Update Website Secrets

**Before making any changes to secrets, save the current database password and any other secret information that will be changed. Store these values in a secure location (such as a password manager or encrypted file) so you can revert to the previous database instance if the process fails.**

- Go to **Secrets Manager**.
- Edit the Secrets for website infrastructure:
  - Update `DATABASE_HOSTNAME` to the restored RDS endpoint. (Find this in RDS > Databases > [your restored DB] > Connectivity & security -> Endpoint)
  - Update `DATABASE_PASSWORD` to the new RDS master password you set or generated during the restore or modification process. If you used the auto-generate option, copy the password when prompted and save it in your secrets or environment configuration. This password is not managed by AWS Secrets Manager for the RDS instance itself, but your application still needs it in its own secrets store.
- Save changes.

### 3a.Auto-Generate and Retrieve RDS Password

- You need to generate a new password for your RDS instance:
  - Go to **AWS Console > RDS > Databases**.
  - Select your RDS instance.
  - Click **Modify**.
  - In the password section, select **Auto generate a password**.
  - Copy the generated password before confirming the modification (you will not be able to see it again).
  - Complete the modification process.
  - Immediately update your secret in **Secrets Manager** with the new password value.
  - Save changes.

### 3b. Import the New RDS Instance into Terraform

- After creating or restoring your RDS instance, import it into Terraform state:
  1. Get the new RDS instance identifier from the AWS Console.
  2. In your `infra` directory, run:
     ```bash
     terraform state rm module.app.aws_db_instance.defualt
     terraform import 'module.app.aws_db_instance.default' <your-rds-identifier>
     ```
  3. Run `terraform plan` to verify Terraform recognizes the imported instance.

### 4. Redeploy ECS Service

- Go to **ECS > Clusters > [your cluster] > Services > [your service]**.
- Click **Update Service > Force new deployment**.
- Confirm redeployment.

### 5. Verify Website Functionality

- Check website and admin for expected data.
- Review ECS logs for database connection errors.
- Confirm users can access the site.

### 6. Rollback (if needed)

- If issues occur, revert secrets/config to previous database values.
- Redeploy ECS service again.

### 7. Cleanup and Documentation

- Optionally, delete the old RDS instance after confirming the new one works.
- Delete old database if no longer needed.
- Update this document with any changes or lessons learned.

---

## DynamoDB State Digest Troubleshooting

If you encounter a Terraform remote state error related to DynamoDB digest mismatch (for example, after restoring or manually editing state), update the digest value in the DynamoDB table:

1. Open the AWS Console and navigate to **DynamoDB** > Tables.
2. Find the table used for Terraform state locking (e.g., `terraform-lock`).
3. Select the Table > Actions > Explore items.
4. Locate the item for your workspace/environment.
5. Edit the `digest` attribute to match the value shown in the Terraform error message.
6. Save the changes and retry your Terraform command.

This step is sometimes necessary after manual RDS replacement or state restoration to resolve Terraform state errors.
