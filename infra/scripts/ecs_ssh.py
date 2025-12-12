#!/usr/bin/env python3
"""
Script to connect to a running ECS container in the sandbox environment via SSH.

Usage:
    source ./.venv/bin/activate
    python infra/scripts/ecs_ssh.py
"""

from sys import exit
from subprocess import run, CalledProcessError
from boto3 import Session
from botocore.exceptions import ClientError, NoCredentialsError
from os import environ


AWS_CLI_PROFILE_NAME: str = environ.get("AWS_PROFILE", "error")
CLUSTER_NAME: str = "sandbox-website-cluster"
SERVICE_NAME: str = "sandbox-website-service"
CONTAINER_NAME: str = "sandbox-website-container"

session = Session(profile_name=AWS_CLI_PROFILE_NAME)
ecs_client = session.client("ecs", region_name="us-east-1")


def get_running_task_arn() -> str | None:
    """Get the ARN of a running task in the sandbox ECS cluster."""
    try:
        response = ecs_client.list_tasks(
            cluster=CLUSTER_NAME, serviceName=SERVICE_NAME, desiredStatus="RUNNING"
        )
        if not response["taskArns"]:
            print(f"ERROR: No running tasks found in cluster {CLUSTER_NAME}")
            exit(1)
        return response["taskArns"][0]
    except ClientError as e:
        print(f"AWS error: {e}")
        exit(1)
    except NoCredentialsError:
        print("ERROR: No AWS credentials found")
        exit(1)


def connect_to_container(task_arn: str) -> None:
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
        run(cmd, check=True)
        print("ECS session closed.")
    except CalledProcessError:
        print(
            "ERROR: Failed to connect to ECS container, check enable_execute_command and policy"
        )
        exit(1)


def main():
    """Main function to connect to ECS container."""
    print("Fetching ECS task ARN...")
    task_arn = get_running_task_arn()
    print(f"Connecting ECS task: {task_arn}...")
    connect_to_container(task_arn)


if __name__ == "__main__":
    main()
