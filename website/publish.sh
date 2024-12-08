#!/bin/bash

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="684212469706"
ECR_REPO_NAME="website-wagtail"
IMAGE_TAG="latest"
IMAGE_NAME="website-wagtail"

# Get the ECR login password and login to ECR
echo "Logging in to Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build the Docker image
echo "Building the Docker image..."
docker build --platform linux/amd64 -t $IMAGE_NAME:$IMAGE_TAG .

# Tag the Docker image with the ECR repository URL
echo "Tagging the Docker image..."
docker tag $IMAGE_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$IMAGE_TAG

# Push the Docker image to ECR
echo "Pushing the Docker image to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$IMAGE_TAG

echo "Image pushed to ECR successfully!"
