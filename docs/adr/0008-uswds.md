# Using USWDS

## Status

Accepted

## Context

USWDS is a css framework maintained by the us government to provide an accessible collection of components that government websites could use to help maintain a consistent look and feel across all government websites.  The tax court already uses USWDS for DAWSON (their case management system).

USWDS is built using SASS and comes with a pre existing compile process well documented in their guides.  SASS allows us to easily customize USWDS in regards to colors, padding, margins, etc if needed.

Additionally, there are some wrappers over USWDS that can be used for Django: django-designstandards and django-uswds-forms.  Both of these wrappers are either Stale or Achieved.

USWDS is not mandated for this project. If we decided we'd rather use Tailwind or our own type of component system, that is not out of the question.

## Decision

We decided to move forward using the default USWDS configuration with SASS.  We avoided the django frameworks because both of those projects are not maintained.  Overall, we feel that just using USWDS has described in their documentation will make for a more maintainble project in the long run.  We've used SASS before and we think it's a very powerful abstraction on top of css that provides a lot of useful utility functions.

Using USWDS over rolling our own is recommended because USWDS is actively maintained which is a healthy sign for using it as a dependency for our project.

## Consequences

To use and compile USWDS, you need node, Gulp, and SASS.  Since our project is in Python, this bring in another whole ecosystem of tooling we'll need to maintain and update over time.
