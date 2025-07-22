# 16. Rules PDF Management

Date: 2025-07-22

## Status

Accepted

## Context

The Tax Court is consolidating hosted rules files.

## Decision

Instead of potentially providing out of date rules onine, one set of complete rules and one document per rule with the following naming convention: rule-{number}.pdf. When rules are updated, rules pdfs can be updated through the admin portal. Since we have document references rather than hard-coded links throughout the code, this will automaticaly update all references to the document to provide the latest version.

## Consequences

Rules documents will remain consistent and up to date throughout the website.
