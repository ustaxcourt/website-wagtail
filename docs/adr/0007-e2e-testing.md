# Choose E2E Testing Framework for Wagtail Python Project

## Status

Proposed

## Context

We want to establish an E2E testing strategy that considers:

- Application architecture built entirely in Python using Wagtail.
- Need for reliable test execution recordings for debugging and documentation.
- Team's existing expertise with Cypress from Dawson project.
- Test framework setup and maintenance overhead.
- Long-term maintainability and developer productivity.

The main consideration is whether to leverage our existing Cypress expertise or transition to Playwright, which is often recommended for end to end testing on Python projects.

## Decision

We propose to continue using Cypress for E2E testing of our Wagtail application.

Key factors influencing this decision:
1. **Team Expertise:**
   - Extensive experience with Cypress across other projects
   - Established testing patterns and shared utilities

2. **Feature Requirements:**
   - Built-in video recording capability in Cypress
   - Advanced debugging tools and time-travel feature
   - Robust test retry mechanisms
   - Interactive test runner out of the box

3. **Project Architecture:**
   - While Wagtail is Python-based, the frontend testing needs remain similar
   - Cypress can effectively test Wagtail's interface and frontend components

## Consequences

Using Cypress for our Wagtail project brings significant advantages through team familiarity, built-in video recording, and robust debugging tools, though it requires maintaining both Node.js and Python environments. While this dual-runtime setup adds some complexity to our CI/CD pipeline, the benefits of leveraging existing team expertise and Cypress's superior features outweigh the overhead of configuring Playwright and dealing with its known issues in test stability and video recording. To mitigate the challenges of the dual-runtime environment, we will establish clear documentation for setup processes and testing patterns specific to our Wagtail implementation.
