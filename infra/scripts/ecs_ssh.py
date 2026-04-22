#!/usr/bin/env python3
"""
Script to connect to a running ECS container using `aws ecs execute-command`
(ECS Exec via AWS Systems Manager Session Manager).

Discovers available website clusters in the current AWS account and prompts
the user to select one if multiple are found.

Prerequisites:
    - AWS CLI configured with the target profile/account
    - ECS Exec enabled for the task/service
    - Session Manager plugin installed for the AWS CLI

Usage:
    source ./.venv/bin/activate
    python infra/scripts/ecs_ssh.py
"""

from sys import exit
from subprocess import run, CalledProcessError
from boto3 import Session
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
from os import environ

CLUSTER_SUFFIX: str = "-website-cluster"
SERVICE_SUFFIX: str = "-website-service"
CONTAINER_SUFFIX: str = "-website-container"

AWS_CLI_PROFILE_NAME: str | None = environ.get("AWS_PROFILE")

try:
    session = (
        Session(profile_name=AWS_CLI_PROFILE_NAME)
        if AWS_CLI_PROFILE_NAME
        else Session()
    )
except ProfileNotFound:
    print(f"ERROR: AWS profile '{AWS_CLI_PROFILE_NAME}' not found")
    exit(1)
ecs_client = session.client("ecs", region_name="us-east-1")


def get_website_clusters() -> list[str]:
    """Return all cluster names matching the website cluster naming convention."""
    try:
        arns: list[str] = []
        paginator = ecs_client.get_paginator("list_clusters")
        for page in paginator.paginate():
            arns.extend(page["clusterArns"])

        names = [arn.split("/")[-1] for arn in arns]
        return sorted(name for name in names if name.endswith(CLUSTER_SUFFIX))
    except ClientError as e:
        print(f"AWS error: {e}")
        exit(1)
    except NoCredentialsError:
        print("ERROR: No AWS credentials found")
        exit(1)


def select_cluster(clusters: list[str]) -> str:
    """Prompt the user to select a cluster if more than one is available."""
    if len(clusters) == 1:
        print(f"Found cluster: {clusters[0]}")
        return clusters[0]

    print("Multiple website clusters found:")
    for i, name in enumerate(clusters, start=1):
        print(f"  {i}) {name}")

    while True:
        raw = input(f"Select a cluster [1-{len(clusters)}]: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(clusters):
            return clusters[int(raw) - 1]
        print("Invalid selection, please try again.")


def get_running_task_arn(cluster_name: str, service_name: str) -> str:
    """Get the ARN of a running task in the given ECS cluster."""
    try:
        response = ecs_client.list_tasks(
            cluster=cluster_name, serviceName=service_name, desiredStatus="RUNNING"
        )
        if not response["taskArns"]:
            print(f"ERROR: No running tasks found in cluster {cluster_name}")
            exit(1)
        return response["taskArns"][0]
    except ClientError as e:
        print(f"AWS error: {e}")
        exit(1)
    except NoCredentialsError:
        print("ERROR: No AWS credentials found")
        exit(1)


def connect_to_container(cluster_name: str, container_name: str, task_arn: str) -> None:
    """Connect to the ECS container using AWS CLI."""
    cmd = [
        "aws",
        "ecs",
        "execute-command",
        *(["--profile", AWS_CLI_PROFILE_NAME] if AWS_CLI_PROFILE_NAME else []),
        "--cluster",
        cluster_name,
        "--task",
        task_arn,
        "--container",
        container_name,
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
    clusters = get_website_clusters()

    if not clusters:
        print(
            f"ERROR: No website clusters found (looking for '*{CLUSTER_SUFFIX}') in AWS profile '{AWS_CLI_PROFILE_NAME or 'default'}'"
        )
        exit(1)

    cluster_name = select_cluster(clusters)
    env_prefix = cluster_name[: -len(CLUSTER_SUFFIX)]
    service_name = f"{env_prefix}{SERVICE_SUFFIX}"
    container_name = f"{env_prefix}{CONTAINER_SUFFIX}"

    print("Fetching ECS task ARN...")
    task_arn = get_running_task_arn(cluster_name, service_name)
    print(f"Connecting to ECS task: {task_arn}...")
    connect_to_container(cluster_name, container_name, task_arn)


if __name__ == "__main__":
    main()
