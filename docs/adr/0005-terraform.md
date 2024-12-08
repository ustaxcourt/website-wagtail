# 5. Terraform

Date: 2024-12-02

## Status

Pending

## Context

Because of the needs to easily deploy to different AWS environments, such as a development aws account, staging, and production, using an infrastructure as code tool would make the entire deployment process repeatable.

## Decision

We decided to go with Terraform for a couple of reasons.  One, the Tax Court already uses Terraform extensively in their Dawson project; this means more in house experience, including experience from Flexion side.  Additionally,  Terraform is currently has the largest community in regards to IaC tooling and cloud support.  Terraform has a ton of community build modules you can easily utilize for deploying anything you might need into AWS.  It also has a very forgiving process for detecting and correctin drift (that is, if someone changing an AWS resource manually); usually it'll just revert any manual changes to match the terraform definitions.


## Consequences

Terraform can have a learning curve to it.
