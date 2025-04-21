# 12. Static Assets

Date: 2025-04-14

## Status

Accepted

## Context

We want to answer the following question:

### What's the best practice for hosting Wagtail websites on AWS using S3 as a file store for Wagtail static files? "Static" files - that is, files that appear in the static/ folder (e.g. static/wagtailadmin/js/vendor.58198f9a6d5c.js) - do not appear to be served by S3. Should they be?

The maintainers of whitenoise argue that serving the static assets using whitenoise should be fine, especially if you host behind a CDN.  I think this means we should at least bring in cloudfront and put it in front of our deployed app.

Adding the collectstatic to the ci/cd pipeline to store the files in s3 increased the deploy time by 10 minutes.  It has to push a ton of files to the bucket on deploy which is a lot slower than just bundling them into the built image.  I think also having the built image means there is a strong 1-to-1 between the wagtail code and the static assets for that build which may be benefitical.

The whitenoise mention that storing the assets to s3 isn't a good idea https://ustc-isd.monday.com/boards/7540668984/views/162628865/pulses/8732485565.


###  Other static files include our media files (e.g. documents) that are accessible via two url patterns: wagtail document URL, https://dev-web.ustaxcourt.gov/documents/332/Rule-39.pdf and public S3 object URL, https://dev-ustc-website-assets.s3.us-east-1.amazonaws.com/documents/Rule-39.pdf Is this appropriate, or should we only use the "wagtail document URL"? What are the best practices?

Putting this document url in front of cloudfront could help allow all these pdfs to be cached and save money in the long run for the court.  Additionally, a user wouldn't need to know we are using s3 which is good from a security perspective.  It also allows us to add WAF rules to rate limit document downloads if needed.

### Are any production-specific, best practice configuration settings necessary that are are distinct from what we currently do in our staging & sandbox environments? Is there anything that we're missing?

I think our approach is good but could use some tweaking if we want to provide faster load times for users.

## Decision

Keep the static assets in the docker image and hosted with whitenoise, and probably put cloudfront in front of it.

## Consequence

- We will need to add a cloudfront distribution to serve the static assets.
