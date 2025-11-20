#!/usr/bin/env python3
"""
Script to connect to a running ECS container in the sandbox environment via SSH.

Usage:
    source ./.venv/bin/activate
    python infra/scripts/ecs_ssh.py
"""

import sys
import subprocess
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


AWS_CLI_PROFILE_NAME: str = "ustc-sso-profile"
CLUSTER_NAME: str = "sandbox-website-cluster"
SERVICE_NAME: str = "sandbox-website-service"
CONTAINER_NAME: str = "sandbox-website-container"

session = boto3.Session(profile_name=AWS_CLI_PROFILE_NAME)
ecs_client = session.client("ecs", region_name="us-east-1")


def get_running_task_arn() -> str:
    """Get the ARN of a running task in the sandbox ECS cluster."""
    try:
        response = ecs_client.list_tasks(
            cluster=CLUSTER_NAME, serviceName=SERVICE_NAME, desiredStatus="RUNNING"
        )
        if not response["taskArns"]:
            print(f"ERROR: No running tasks found in cluster {CLUSTER_NAME}")
            sys.exit(1)
        return response["taskArns"][0]
    except ClientError as e:
        print(f"AWS error: {e}")
        sys.exit(1)
    except NoCredentialsError:
        print("ERROR: No AWS credentials found")
        sys.exit(1)


def connect_to_container(task_arn: str):
    """Connect to the ECS container using AWS CLI."""
    cmd = [
        "aws",
        "ecs",
        "execute-command",
        "--profile",
        AWS_CLI_PROFILE_NAME,
        "--cluster",
        CLUSTER_NAME,
        "--task",
        task_arn,
        "--container",
        CONTAINER_NAME,
        "--interactive",
        "--command",
        "/bin/bash",
    ]

    try:
        subprocess.run(cmd, check=True)
        print("ECS session closed.")
    except subprocess.CalledProcessError:
        print("ERROR: Failed to connect to ECS container")
        print("Make sure the task definition has executeCommandConfiguration enabled")
        sys.exit(1)


def main():
    """Main function to connect to ECS container."""
    print("Connecting to sandbox ECS container...")
    task_arn = get_running_task_arn()
    print(f"Connecting to task: {task_arn}")
    connect_to_container(task_arn)


if __name__ == "__main__":
    main()
