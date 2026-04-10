# 22. Wagtail Transfer

Date: 2026-03-31

## Status

Drafting

## Context

There is a need within the application to be able to copy pages, snippets, and referenced images and documents from one environment to another to ensure those objects are the same across the environments. This need allows a page to be created and validated in a lower environment and then be copied to a higher environment without the risk that the page's designer may accidentally alter the page's content when trying to recreate the page. It also allows a page from a higher environment to be copied to a lower environment for troubleshooting purposes.

Wagtail Transfer is an open-source library that handles the heavy lifting in performing such a transfer between Wagtail environments once properly configured. Environments are configured as source/destination pairs with transfers initiated from the destination environment. Those with permissions to initiate such a transfer are able to choose the source environment, which page, snippet, folder of pages, or collection of snippets they would like to transfer, and the folder in the destination environment in which the page(s) will be copied to.

## Decision

We will use Wagtail Transfer to perform the transfers of pages, snippets, and any images and documents they reference. We chose this approach because writing our own library to do this functionality would have to solve many of the same problems (e.g., how to determine if a page being transferred already exists in the destination environment, how to handle duplicate page slugs, how to determine what is being referenced by a page, etc.) that are already addressed by Wagtail Transfer.

## Consequences

Wagtail Transfer requires the source environment to have the setting WAGTAILTRANSFER_SECRET_KEY set and the destination environment to have the setting WAGTAILTRANSFER_SOURCES set in order to work. WAGTAILTRANSFER_SOURCES is a JSON string that contains the user-recognizable name of the source environment and the source environment's WAGTAILTRANSFER_SECRET_KEY. Both of these settings hold secret values that should be retrieved from a Secrets Manager. Wagtail requires settings to be loaded at the time the Wagtail site is initialized. These two requirements together have led us to save the WAGTAILTRANSFER_SOURCES and WAGTAILTRANSFER_SECRET_KEY values in the "ecs-task-secrets-XYZ" secret of AWS Secrets Manager, where XYZ is a string of numbers, to update the Terraform scripts for building the container running Wagtail in ECS to set environment variables within the container with these two values, and to update the Wagtail settings file to retrieve these values from the environment variables.

Initial testing of Wagtail Transfer identified several actions that Wagtail Transfer can not do, including:
- Copy images or documents from one environment to the other directly.
- Update existing images in an environment if Wagtail Transfer did not create the image.
- Transfer a page with a new component type that does not exist in the destination environment.
- Transfer reports.
- Transfer settings of one environment to another.
- Copy a page’s revisions or information about the user that created it when the page is transferred.
- Add or remove source environments from within the Wagtail Admin interface.
- Automatically sort the list of environments that data can be transferred from.

None of the above actions are strictly necessary to be able to do the type of transfers we want to perform. Adjustments to other Wagtail Transfer settings, such as WAGTAILTRANSFER_LOOKUP_FIELDS or WAGTAILTRANSFER_NO_FOLLOW_MODELS, may allow us to overcome these limitations in the future.
