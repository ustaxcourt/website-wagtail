# Running the Wagtail Website

After cloning the repo, you'll need to make sure you have python3 installed along with pip3.

- `cd website`
- `python3 -m venv env`
- `source env/bin/activate`
- `pip3 install -r requirements.txt`
- `python3 manage.py migrate` (only needed once unless new models added)
- `python3 manage.py createsuperuser` (only run once)
- `python3 manage.py runserver`

# The Developer Sandbox AWS Account

## Getting AWS Credentials

Mike will reach out to you with a aws console username & password. Please verify you can login with it, and also reach out to have your default password changed because you can't do it in the console from what we've seen.

Next, you'll want to make sure your application is setup with your sso. You should be able to run this command and enter your SSO url when prompted. You'll also be promted with some other stuff you want to fill in.

- `aws sso configure`

If you want to manually refresh your token which should last 8 hours, run this command

- `aws sso login --profile sandbox`

## Deploying to your account

If you want to deploy the application to your sandbox, follow these steps:

prereqs: - install terraform (we recommend `brew install tfenv`) - install aws cli

1. `cd infra`
2. `./setup-tf-buckets.sh` (only run once on a brand new sandbox)
3. `./deploy.sh` (re-run after any terraform changes to test)

## Destroying (assuming you've deployed at least once)

1. `cd infra`
2. `./destroy.sh`

## Cavets

If you run a terraform init with your sandbox account, but then try to run it again for another account, remember to delete the infra/.terraform directory otherwise you'll run into state issues. After deleting that directory, terraform will reconfigure the backend state from s3 to your local machine instead of re-using the existing local state file.

## Manually Connecting to DB

Because the RDS instance is behind a VPS, that means you will need to setup an SSH tunnel through a bastion host to be able to access it.

`ssh -L 5432:<RDS_HOSTNAME>:5432 -N -i ~/.ssh/id_ed25519 ubuntu@<IP_ADDRESS>`

after running this in a separate terminal, you should be able to run migrations or connect directly using tableplus.
