# 18. AWS SES for Wagtail's Email Backend
Date: 2025-09-04

## Status
Accepted

## Context
Our Wagtail application requires an email backend to handle various transactional emails, such as user password resets, form submission confirmations, and administrative notifications. We evaluated two primary AWS services for this purpose: Simple Email Service (SES) and Simple Notification Service (SNS).

AWS SES is a cloud-based email sending service designed to help digital marketers and application developers send marketing, notification, and transactional emails. It is a dedicated service for handling email.

AWS SNS is a fully managed publish/subscribe messaging service that enables decoupling of microservices, distributed systems, and serverless applications. It can deliver messages to a variety of endpoints, including email, SMS, SQS queues, and Lambda functions.

Our current and foreseeable application requirements are strictly limited to sending email notifications. We do not have any features on our roadmap that would require other notification channels like SMS or mobile push notifications. The primary need is for a reliable, scalable, and cost-effective solution for sending emails directly from our Wagtail application.

## Decision
We will use AWS SES as the email backend for our Wagtail application.

This decision is based on the principle of selecting the simplest tool that directly addresses the requirement. Since our only need is to send emails, SES is the most direct and fitting solution. Using SNS would introduce the unnecessary complexity of a pub/sub system for a simple point-to-point email delivery task. SES provides all the necessary features for our use case—including sending transactional emails, managing sender identities, and monitoring email delivery—without the overhead of a multi-channel notification system.

## Consequences
By choosing SES, we gain a straightforward and cost-effective email solution that is easy to configure and maintain within the Django/Wagtail ecosystem. The development team can integrate it using standard Django email backend settings with minimal effort.

The primary consequence is that if our requirements were to expand in the future to include other notification types (e.g., SMS, push notifications), we would need to integrate an additional service like SNS at that time. This would require a new architectural decision and development effort to refactor the notification logic. However, given our current roadmap, this is a low and acceptable risk, and it prevents us from over-engineering our current solution for a hypothetical future need.
