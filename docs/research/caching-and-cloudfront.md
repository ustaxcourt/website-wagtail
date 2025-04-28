# CloudFront Implementation Research

## Overview

This document summarizes research and considerations for implementing AWS CloudFront in front of our S3 bucket and Wagtail application. It covers both the benefits of CloudFront and architectural considerations for securing our infrastructure.

## CloudFront Benefits

### 1. Performance and Cost Optimization
- **Edge Caching**: CloudFront caches content at edge locations worldwide, reducing latency for users.  Maybe assets in our application, such as images, script files, etc would benefit from this form of caching since I doubt they would change often.
- **Reduced Origin Load**: By serving cached content from edge locations, we reduce the load on our origin servers.  This means if we find that users are doing more requests than our wagtail instance can handle, increasing the caching could be one approach to reduce this load.
- **Cost Savings**: Caching frequently accessed content can significantly reduce data transfer costs from S3 and ALB. Based on typical usage patterns:
  - S3 data transfer costs $0.09/GB, while CloudFront transfer is around $0.085/GB
  - For 1TB monthly traffic, this could save ~$50/month on transfer costs alone
  - Cache hit rates of 80-90% can reduce origin requests by 4-5x, lowering ALB costs
  - Document downloads (PDFs) being cached could save significant bandwidth costs given their larger size
  - Static assets (JS, CSS, images) being cached reduces load on Wagtail servers

### 2. Security Enhancements
- **WAF Integration**: CloudFront provides seamless integration with AWS WAF for protecting against common web exploits
- **DDoS Protection**: Built-in DDoS protection through AWS Shield Standard
- **SSL/TLS Termination**: Handles SSL/TLS termination at the edge, reducing load on origin servers

### 3. Flexible Caching Configuration
- **Path-Based Caching Rules**: Different caching behaviors can be configured for different URL patterns
- **Custom Cache Keys**: Ability to create cache keys based on headers, cookies, or query strings
- **TTL Control**: Fine-grained control over cache duration for different content types
- **Cache Invalidation**: Ability to invalidate specific paths or patterns when content updates

## Architectural Considerations

### Private Subnet and VPC Origin Approach
- **Security**: Moving ALB to private subnet prevents direct internet access, reducing attack surface
- **CloudFront as Single Entry Point**: All traffic enters through CloudFront, providing a consistent security boundary
- **Origin Access Control**: CloudFront can be configured to only accept traffic from specific CloudFront distributions
- **Network Isolation**: Private subnets provide additional layer of security for internal resources

### S3 Access Patterns
- **Direct S3 Access**: Currently, S3 objects are accessible via both Wagtail URLs and direct S3 URLs
- **Security Implications**: Direct S3 access bypasses potential security controls and monitoring
- **CloudFront Solution**: Using CloudFront as the only access point for S3 content provides:
  - Consistent access patterns
  - Centralized security controls
  - Better monitoring and logging
  - Ability to implement rate limiting and access controls

## Implementation Considerations

### Static Assets
- **Current Approach**: Static assets are served through Whitenoise in the Docker image
- **CloudFront Benefits**:
  - Caching of static assets at edge locations
  - Reduced load on application servers
  - Potential for longer cache durations for static content

### Media Files
- **Current State**: Media files accessible via both Wagtail and direct S3 URLs
- **CloudFront Solution**:
  - Single access point for all media
  - Consistent URL patterns
  - Ability to implement caching strategies
  - Potential for implementing download restrictions

## Decision Factors

### Pros of CloudFront Implementation
1. Improved performance through edge caching
2. Enhanced security through WAF and DDoS protection
3. Cost optimization through reduced origin load
4. Flexible caching configuration
5. Single entry point for all content
6. Better control over access patterns

### Cons of CloudFront Implementation
1. Additional complexity in configuration
2. Need to manage cache invalidation
3. Potential for serving stale content if not properly configured
4. Additional AWS service to monitor and maintain

## Conclusion

The implementation of CloudFront offers significant benefits in terms of performance, security, and cost optimization. The ability to configure different caching behaviors for different content types, combined with the security benefits of WAF integration and private subnet architecture, makes CloudFront a compelling solution for our needs.

The decision to implement CloudFront should be weighed against the additional complexity it introduces, but the benefits of improved security, performance, and cost optimization suggest it would be a valuable addition to our architecture.
