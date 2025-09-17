# 19. Using django-ses for AWS SES Integration
Date: 2025-09-04

## Status
Accepted

## Context
Following our decision in ADR-14 to use AWS SES for our email backend, we need to determine the best method for integrating SES with our Wagtail/Django application. There are two primary approaches:

Using Django's built-in SMTP Backend: Configure Django's django.core.mail.backends.smtp.EmailBackend with the SMTP credentials provided by AWS SES. This method requires no additional third-party libraries.

Using a dedicated library: Incorporate a third-party Django library that leverages the AWS SDK (boto3) to send emails via the SES API. django-ses is a popular, well-maintained library for this purpose.

While the SMTP approach works, using the SES API directly via a library like django-ses is often more robust. API calls can provide more detailed feedback on send status, are typically faster, and can more seamlessly integrate with AWS IAM roles for authentication, avoiding the need to manage static SMTP credentials.

## Decision
We will use the django-ses library as the email backend to integrate our Wagtail application with AWS SES.

This decision favors a more native and robust integration with the AWS ecosystem. By using django-ses, we leverage the boto3 SDK, which is the standard for interacting with AWS services in Python. This allows for more secure authentication via IAM roles, provides better performance, and offers more granular error reporting than the generic SMTP protocol.

## Consequences
By adding django-ses to our project, we introduce a new third-party dependency that must be managed and kept up-to-date. This also includes its dependencies, most notably boto3.

The positive consequence is a more reliable, secure, and maintainable integration. Configuration is simplified, especially in production environments running on AWS infrastructure, as we can grant our application an IAM role with ses:SendEmail permissions instead of storing and rotating SMTP user credentials. This aligns with AWS best practices and strengthens our security posture.
