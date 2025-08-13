import os
import time

import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand

# The AWS region where your SES service is configured.
AWS_REGION = "us-east-1"


class Command(BaseCommand):
    """
    A Wagtail management command to verify a domain with AWS SES.

    This command automates the following steps:
    1. Reads a domain name from the 'DOMAIN_NAME' environment variable.
    2. Generates DKIM verification tokens from AWS SES for the domain.
    3. Finds the corresponding Hosted Zone in Route 53.
    4. Creates the necessary CNAME records in Route 53 for DKIM verification.
    5. Polls SES to check for successful verification status.
    """

    help = "Verifies a domain with AWS SES and adds DKIM records to Route 53."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ses_client = self._create_boto_client("ses")
        self.route53_client = self._create_boto_client("route53")

    def _create_boto_client(self, service_name):
        """Creates and returns a boto3 client for a given AWS service."""
        try:
            client = boto3.client(service_name, region_name=AWS_REGION)
            return client
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"❌ Error creating {service_name} client: {e}")
            )
            return None

    def handle(self, *args, **options):
        """The main execution method for the management command."""
        self.stdout.write(
            self.style.SUCCESS("--- Automated AWS SES & Route 53 Domain Setup ---")
        )

        domain_to_verify = os.getenv("DOMAIN_NAME")
        if not domain_to_verify:
            self.stderr.write(
                self.style.ERROR(
                    "Error: The 'DOMAIN_NAME' environment variable is not set."
                )
            )
            return

        if not self.ses_client or not self.route53_client:
            self.stderr.write(
                self.style.ERROR("Could not create AWS clients. Aborting.")
            )
            return

        # Step 1: Get DKIM tokens from SES
        tokens = self._get_dkim_tokens(domain_to_verify)

        # Step 2: Add DNS records to Route 53
        if tokens is not None:  # Note: tokens can be an empty list
            success = self._add_records_to_route53(domain_to_verify, tokens)

            # Step 3: Check SES for verification status
            if success:
                self._check_verification_status(domain_to_verify)

        self.stdout.write(self.style.SUCCESS("\n--- Script Finished ---"))

    def _get_dkim_tokens(self, domain):
        """Starts SES domain verification and returns the DKIM tokens."""
        self.stdout.write(
            f"\n1. Attempting to generate DKIM records for '{domain}' from SES..."
        )
        try:
            response = self.ses_client.verify_domain_dkim(Domain=domain)
            dkim_tokens = response.get("DkimTokens", [])

            if not dkim_tokens:
                self.stdout.write(
                    self.style.WARNING(
                        "Could not retrieve DKIM tokens. The domain might already be verified."
                    )
                )
                return []

            self.stdout.write(
                self.style.SUCCESS("✅ Success! Generated the following DKIM tokens:")
            )
            for token in dkim_tokens:
                self.stdout.write(f"   - {token}")
            return dkim_tokens

        except ClientError as e:
            self.stderr.write(
                self.style.ERROR(f"❌ SES Error: {e.response['Error']['Message']}")
            )
            return None

    def _add_records_to_route53(self, domain, dkim_tokens):
        """Finds the domain's hosted zone and adds the DKIM CNAME records."""
        if not dkim_tokens:
            self.stdout.write("\nNo DKIM tokens to add. Skipping Route 53 update.")
            return True # Considered success as there's nothing to do

        self.stdout.write(f"\n2. Attempting to add records to Route 53 for '{domain}'...")
        try:
            # Find the Hosted Zone ID for the domain
            zones_response = self.route53_client.list_hosted_zones()
            hosted_zone_id = next(
                (
                    zone["Id"]
                    for zone in zones_response["HostedZones"]
                    if zone["Name"].rstrip(".") == domain
                ),
                None,
            )

            if not hosted_zone_id:
                self.stderr.write(
                    self.style.ERROR(
                        f"❌ Route 53 Error: Could not find a Hosted Zone for '{domain}'."
                    )
                )
                self.stderr.write(
                    "   Please ensure the domain is managed by Route 53 in this AWS account."
                )
                return False

            self.stdout.write(f"   Found Hosted Zone ID: {hosted_zone_id}")

            # Construct the change batch for the API call
            changes = [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": f"{token}._domainkey.{domain}",
                        "Type": "CNAME",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": f"{token}.dkim.amazonses.com"}],
                    },
                }
                for token in dkim_tokens
            ]

            # Submit the changes to Route 53
            change_batch_response = self.route53_client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id, ChangeBatch={"Changes": changes}
            )
            change_id = change_batch_response["ChangeInfo"]["Id"]
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Success! Submitted change batch to Route 53. Change ID: {change_id}"
                )
            )
            return True

        except ClientError as e:
            self.stderr.write(
                self.style.ERROR(f"❌ Route 53 Error: {e.response['Error']['Message']}")
            )
            return False

    def _check_verification_status(self, domain, retries=10, delay=30):
        """Checks the DKIM verification status of a given domain with a timeout."""
        self.stdout.write(
            f"\n3. Checking DKIM verification status in SES for '{domain}'..."
        )
        self.stdout.write(f"   Checking every {delay} seconds for up to {retries * delay / 60:.1f} minutes.")

        for attempt in range(retries):
            try:
                response = self.ses_client.get_identity_dkim_attributes(Identities=[domain])
                attributes = response["DkimAttributes"].get(domain)

                if not attributes:
                    self.stdout.write("   Could not get attributes yet. Waiting...")
                else:
                    status = attributes["DkimVerificationStatus"]
                    self.stdout.write(f"   Attempt {attempt + 1}/{retries}: Current Status is {status}")

                    if status == "Success":
                        self.stdout.write(
                            self.style.SUCCESS("\n🎉 Domain verified and DKIM setup is complete!")
                        )
                        return
                    elif status == "Failed":
                        self.stderr.write(
                            self.style.ERROR(
                                "\n❗️ Verification failed. Please check the AWS console for details."
                            )
                        )
                        return

            except ClientError as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"❌ SES Error checking status: {e.response['Error']['Message']}"
                    )
                )
                return # Exit on API error

            time.sleep(delay)

        self.stderr.write(
            self.style.ERROR(
                f"\n❗️ Timed out after {retries} attempts. Verification is not yet successful. "
                "It may complete later. Please check the AWS SES Console."
            )
        )