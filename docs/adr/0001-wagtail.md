# 1. Wagtail

Date: 2024-12-02

## Status

Accepted

## Context

We need to allow Tax Court website to be easily updated by internal court moderators and content writers.  There are needs for potential advanced user roles and customization in the future.  After researching various CMS technology, it was decided that Wagtail has a lot of the necessary features to build out the court website, and it's also built ontop of a mature web framework and programming language.

## Decision

We decided to more forward using Wagtail as our CMS system built on top of the Django web framework.  Wagtail has been used in other successful government systems as the CMS option, and Django is a mature framework that has a lot of options built in out of the box.  Additionally, the court has more python experience than other languages.  We believe Wagtail will be a good solution for the court's needs.

Wagtail has the ability to hook into Postgres, one of the most popular databases, and S3 for storing media, assets, images, etc.  Django is built ontop of a powerful ORM which allows easy customization for where external data storage shoud live.

## Consequences
