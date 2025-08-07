import boto3
from botocore.exceptions import ClientError
import time

# Use the desired AWS region for SES
AWS_REGION = "us-east-1"


def create_boto_client(service_name):
    """Creates and returns a boto3 client for a given AWS service."""
    try:
        client = boto3.client(service_name, region_name=AWS_REGION)
        return client
    except Exception as e:
        print(f"❌ Error creating {service_name} client: {e}")
        return None


def verify_domain_and_get_tokens(ses_client):
    """Starts SES domain verification and returns the domain and DKIM tokens."""
    domain = (
        input("Enter the domain you want to verify (e.g., yourdomain.com): ")
        .strip()
        .lower()
    )
    if not domain:
        print("⚠️ Domain cannot be empty. Aborting.")
        return None, None

    print(f"\n1. Attempting to generate DKIM records for '{domain}' from SES...")
    try:
        response = ses_client.verify_domain_dkim(Domain=domain)
        dkim_tokens = response.get("DkimTokens", [])

        if not dkim_tokens:
            print(
                "Could not retrieve DKIM tokens. The domain might already be verified."
            )
            return domain, []

        print("✅ Success! Generated the following DKIM tokens:")
        for token in dkim_tokens:
            print(f"   - {token}")
        return domain, dkim_tokens

    except ClientError as e:
        print(f"❌ SES Error: {e.response['Error']['Message']}")
        return None, None


def add_records_to_route53(route53_client, domain, dkim_tokens):
    """Finds the domain's hosted zone and adds the DKIM CNAME records."""
    if not dkim_tokens:
        print("\nNo DKIM tokens to add. Skipping Route 53 update.")
        return False

    print(f"\n2. Attempting to add records to Route 53 for '{domain}'...")
    try:
        # Find the Hosted Zone ID for the domain
        zones_response = route53_client.list_hosted_zones()
        hosted_zone_id = None
        for zone in zones_response["HostedZones"]:
            # Match 'yourdomain.com.' with 'yourdomain.com'
            if zone["Name"].rstrip(".") == domain:
                hosted_zone_id = zone["Id"]
                break

        if not hosted_zone_id:
            print(f"❌ Route 53 Error: Could not find a Hosted Zone for '{domain}'.")
            print(
                "   Please ensure the domain is managed by Route 53 in this AWS account."
            )
            return False

        print(f"   Found Hosted Zone ID: {hosted_zone_id}")

        # Construct the change batch for the API call
        changes = []
        for token in dkim_tokens:
            record_name = f"{token}._domainkey.{domain}"
            record_value = f"{token}.dkim.amazonses.com"
            changes.append(
                {
                    "Action": "UPSERT",  # Creates or updates the record
                    "ResourceRecordSet": {
                        "Name": record_name,
                        "Type": "CNAME",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": record_value}],
                    },
                }
            )

        # Submit the changes to Route 53
        change_batch_response = route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id, ChangeBatch={"Changes": changes}
        )

        change_id = change_batch_response["ChangeInfo"]["Id"]
        print(f"✅ Success! Submitted change batch to Route 53. Change ID: {change_id}")
        return True

    except ClientError as e:
        print(f"❌ Route 53 Error: {e.response['Error']['Message']}")
        return False


def check_verification_status(ses_client, domain):
    """Checks the DKIM verification status of a given domain."""
    if not domain:
        return

    print(f"\n3. Checking DKIM verification status in SES for '{domain}'.")
    print("   This will check every 30 seconds. Press Ctrl+C to stop.")

    try:
        while True:
            response = ses_client.get_identity_dkim_attributes(Identities=[domain])
            attributes = response["DkimAttributes"].get(domain)

            if not attributes:
                print("   Could not get attributes yet. Waiting...")
                time.sleep(30)
                continue

            status = attributes["DkimVerificationStatus"]
            print(f"   Current Status: {status}")

            if status == "Success":
                print("\n🎉 Domain verified and DKIM setup is complete!")
                break
            elif status == "Failed":
                print(
                    "\n❗️ Verification failed. Please check the AWS console for more details."
                )
                break

            time.sleep(30)
    except KeyboardInterrupt:
        print("\nStopped checking status.")
    except ClientError as e:
        print(f"❌ SES Error checking status: {e.response['Error']['Message']}")


if __name__ == "__main__":
    print("--- Automated AWS SES & Route 53 Domain Setup ---")
    ses_client = create_boto_client("ses")
    route53_client = create_boto_client("route53")

    if ses_client and route53_client:
        # Step 1: Get DKIM tokens from SES
        domain_to_verify, tokens = verify_domain_and_get_tokens(ses_client)

        # Step 2: Add DNS records to Route 53
        if domain_to_verify and tokens:
            success = add_records_to_route53(route53_client, domain_to_verify, tokens)

            # Step 3: Check SES for verification status
            if success:
                check_verification_status(ses_client, domain_to_verify)

        print("\n--- Script Finished ---")
