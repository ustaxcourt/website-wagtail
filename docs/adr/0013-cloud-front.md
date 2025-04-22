# 13. Cloudfront

Date: 2025-04-22

## Status

Accepted

## Context

AWS CloudFront is a content delivery network (CDN) service that securely delivers data, videos, applications, and APIs to customers globally with low latency and high transfer speeds. For our application, using CloudFront in front of our Wagtail service and S3 buckets would improve performance by caching content at edge locations closer to users, reduce load on our origin servers, and provide an additional layer of security through integration with AWS WAF.

CloudFront's ordered cache behaviors provide significant flexibility in how we handle different types of content:

1. Our current configuration uses CachingDisabled for dynamic content (default behavior) and a basic static content policy for /files/* paths. This conservative approach ensures correctness during initial deployment.

2. We can easily add more aggressive caching rules in production by:
   - Creating additional ordered cache behaviors for specific URL patterns
   - Adjusting TTL settings (currently 1 hour default, 24 hour max for static content)
   - Implementing custom cache keys based on headers, cookies, or query strings
   - Using CloudFront functions to modify cache keys or implement custom caching logic

For example, if we find our ALB is getting overwhelmed with requests for relatively static pages like the homepage or forms, we could add:


## Decision

We will use CloudFront as our CDN to improve performance, reduce costs through caching, and enhance security by providing a consistent entry point that can be protected with WAF rules while keeping our origin servers private.


## Consequence

Using CloudFront introduces complexity around cache invalidation and debugging since content updates won't be immediately visible and issues may be harder to diagnose. The service requires careful configuration management and monitoring of costs related to request volume, data transfer, and cache invalidations. Security and user experience need special attention to ensure sensitive content isn't cached and users don't see stale content during deployments.
