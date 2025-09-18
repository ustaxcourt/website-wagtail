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
- Configure instance details. Ensure that the configuration settings of the restored snapshot match the original/existing configuration.
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
          - **Important**: Ensure that you specify the same security group(s) that were specified in the database you are replacing. This will also be the same security group used by the websites ECS Cluster.  You can find the secuity group used by the ECS Cluster in the AWS console under `Amazon Elastic Container Service -> Clusters -> [your cluster] -> Services -> [your service] -> Configuration`

    - Under Tags tab
        - Tags – optional

- Launch the instance and wait for it to become available.

### 3. Update Website Secrets

**Before making any changes to secrets, save the current database password and any other secret information that will be changed. Store these values in a secure location (such as a password manager or encrypted file) so you can revert to the previous database instance if the process fails.**

- Go to **Secrets Manager**.
- Edit the Secrets (`website_secrets`) for website infrastructure:
  - Update `DATABASE_HOSTNAME` to the restored RDS endpoint. (Find this in RDS > Databases > [your restored DB] > Connectivity & security -> Endpoint)
  - Update `DATABASE_PASSWORD` to the new RDS master password you set or generated during the restore or modification process. If you used the auto-generate option, copy the password when prompted and save it in your secrets or environment configuration. This password is not managed by AWS Secrets Manager for the RDS instance itself, but your application still needs it in its own secrets store.
- Save changes.
- Now edit the secret with the prefix `ecs-task-secrets-`.
  - update `DATABASE_URL` by replacing the password portion (the string before the `@` symbol) with value used in `DATABASE_PASSWORD`, and the endpoint portion with the value used in `DATABASE_HOSTNAME`


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
- Update this document with any changes or lessons learned.
