# 14. Scheduled Task Execution using EventBridge Scheduler and ECS Fargate

Date: 2025-06-17

## Status

Accepted

## Context

The application requires a reliable and cost-effective method for executing backend tasks on a recurring schedule, such as content publishing or data processing. The solution needs to integrate seamlessly with our existing containerized application infrastructure on AWS ECS. Some options we considered are:

* Use Github actions, we already use Github actions for RDS recovery, deployment and as such we rely heavily on their availability.
* Configure the existing ECS task with CRON or Creating a dedicated EC2 instance with cron.
* Building a separate, simple container service for this purpose.

The chosen solution leverages AWS-native serverless components to avoid managing dedicated compute resources for intermittent tasks.

The implemented architecture uses AWS EventBridge Scheduler to invoke an ECS task on a defined cron schedule. This approach was selected because it allows us to reuse our primary application's existing ECS Task Definition and Docker image. The specific script to be run is injected at runtime using the `containerOverrides` feature within the scheduler's target configuration. This avoids the need to build and maintain separate Docker images for each unique task. The compute layer is AWS Fargate, which provisions serverless capacity only for the duration of the task's execution.

## Decision

We will use AWS EventBridge Scheduler as the standard mechanism for triggering all scheduled and recurring backend jobs. These jobs will run as serverless ECS tasks on our existing Fargate cluster.

This decision leverages several key features:
* **Task Definition Reusability**: We will not create new task definitions for scheduled jobs. Instead, we will reuse the main application's definition and use runtime overrides.
* **Command Overrides**: The `input` parameter on the `aws_scheduler_schedule` resource will be used to specify the exact command the container should run upon startup, for instance, `python manage.py publish_scheduled`.
* **Dedicated IAM Roles**: Each scheduler will use a dedicated IAM role that grants it the precise permissions to run a specific ECS task, adhering to the principle of least privilege.
* **Serverless Compute**: Fargate will be the exclusive compute engine for these tasks, ensuring we do not pay for idle resources.

## Consequences

This serverless approach for scheduled tasks introduces significant benefits but also requires specific operational considerations for deployment.

* **Deployment Race Condition**: There is a risk of failure when tasks are scheduled frequently (e.g., hourly). A race condition can occur if the AWS EventBridge Scheduler and ECR image are updated with new application code before the corresponding database migration is complete. In this scenario, a scheduled ECS task could start with the new code but fail because it cannot find the database models it references.

* **Accepted Risk**: While not ideal, we accept this risk for frequently running tasks. The expectation is that if one execution fails due to a deployment in progress, a subsequent execution will succeed after the migration is finished, effectively allowing the system to self-heal.

* **Future Mitigation Strategy**: In the future, if database migrations begin to take significantly longer (e.g., more than a few minutes), we should enhance our deployment process. This could involve either manually disabling the schedule by setting its state to `"DISABLED"` during deployments or introducing automated steps to handle this gracefully.

* **Pros**:
    * **Cost-Efficiency**: This is a highly cost-effective solution as we only incur costs for Fargate compute when a task is actively running. There are no idle servers.
    * **Reduced Operational Overhead**: Reusing the existing task definition simplifies CI/CD and reduces configuration drift between the main application and its tasks. The serverless nature of Fargate and EventBridge eliminates the need for patching or managing underlying infrastructure.
    * **Scalability and Reliability**: The solution is built on highly available and scalable AWS managed services. The scheduler includes a simple retry policy for transient failures. We had trouble with overly relying on Github actions.

* **Cons**:
    * **Potential for "Cold Starts"**: Fargate tasks can experience a brief startup delay. While generally acceptable for asynchronous background jobs, this could be a factor for tasks that are highly time-sensitive.
    * **Configuration Sensitivity**: As discovered during implementation, the `input` block for the scheduler target is syntactically sensitive. Incorrectly structured JSON can lead to deployment failures that are difficult to diagnose from the initial API error messages.

* **Maintenance and Support**:
    * To add a new scheduled job, an engineer must define a new `aws_scheduler_schedule` resource in Terraform, specifying the new schedule and command override.
    * For verifying the job completion or debugging, check cloudwatch logs.
