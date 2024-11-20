
# The Developer Sandbox AWS Account

## Deploying to your account

If you want to deploy the application to your sandbox, follow these steps:

prereqs:
    - install terraform (we recommend `brew install tfenv`)
    - install aws cli

1. `cd infra`
2. `./setup-tf-buckets.sh` (only run once on a brand new sandbox)
3. `./deploy.sh` (re-run after any terraform changes to test)


## Destroying (assuming you've deployed at least once)

1. `cd infra`
2. `./destroy.sh`

## Cavets

If you run a terraform init with your sandbox account, but then try to run it again for another account, remember to delete the infra/.terraform directory otherwise you'll run into state issues.  After deleting that directory, terraform will reconfigure the backend state from s3 to your local machine instead of re-using the existing local state file.