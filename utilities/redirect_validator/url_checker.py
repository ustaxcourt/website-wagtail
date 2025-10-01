import requests
import csv
import argparse
from urllib.parse import urljoin
import sys


def get_status_emoji(status_code):
    """Returns an emoji based on the HTTP status code."""
    if status_code >= 200 and status_code < 300:
        return "✅"  # Success (e.g., 200 OK)
    elif status_code == 404:
        return "❌"  # Not Found
    elif status_code >= 300 and status_code < 400:
        return "↪️"  # Redirect (though requests follows them, this might indicate an issue if it's the final code)
    elif status_code >= 400 and status_code < 500:
        return "Client Error"  # Other client errors (e.g. 403 Forbidden)
    elif status_code >= 500:
        return "❗"  # Server Error
    else:
        return "🟡"  # Other statuses


def check_urls(base_url, input_csv_path, output_csv_path):
    """
    Reads relative URLs from a CSV, checks their HTTP status, and records redirects.

    Args:
        base_url (str): The base URL to prepend to the relative paths.
        input_csv_path (str): The path to the input CSV file.
        output_csv_path (str): The path for the output CSV report.
    """
    print(f"Starting URL check for base URL: {base_url}")
    print(f"Reading from: {input_csv_path}")

    try:
        # We open both files at the start to ensure we can write to the output file.
        with (
            open(input_csv_path, "r", encoding="utf-8-sig") as infile,
            open(output_csv_path, "w", newline="", encoding="utf-8") as outfile,
        ):
            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            # Write the header row for the output CSV
            writer.writerow(
                [
                    "Result",
                    "Final Status Code",
                    "Original Relative URL",
                    "Full URL Checked",
                    "Final Destination URL",
                    "Redirect Chain",
                ]
            )

            # Skip header row of the input file if it exists
            # next(reader, None) # Uncomment this if your input CSV has a header

            for i, row in enumerate(reader):
                if not row:
                    continue  # Skip empty rows

                relative_url = row[0].strip()
                # Construct the full URL
                full_url = urljoin(base_url, relative_url)

                try:
                    # Make the request. requests handles redirects by default.
                    # We add a User-Agent to mimic a real browser.
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }
                    response = requests.get(
                        full_url, headers=headers, timeout=15, allow_redirects=True
                    )

                    final_url = response.url
                    status_code = response.status_code
                    emoji = get_status_emoji(status_code)

                    # Build a string representing the redirect chain
                    redirect_chain = ""
                    if response.history:
                        chain = []
                        for resp in response.history:
                            chain.append(f"{resp.url} ({resp.status_code})")
                        chain.append(f"{final_url} ({status_code})")
                        redirect_chain = " -> ".join(chain)
                    else:
                        redirect_chain = "No redirects"

                    # Write the results to the output file
                    writer.writerow(
                        [
                            emoji,
                            status_code,
                            relative_url,
                            full_url,
                            final_url,
                            redirect_chain,
                        ]
                    )
                    print(f"{emoji} SUCCESS: {full_url} -> {final_url} ({status_code})")

                except requests.exceptions.RequestException as e:
                    # Handle network errors, timeouts, etc.
                    error_message = str(e)
                    writer.writerow(
                        ["❗", "N/A", relative_url, full_url, "Error", error_message]
                    )
                    print(f"❗ ERROR: {full_url} - {error_message}", file=sys.stderr)

    except FileNotFoundError:
        print(
            f"FATAL ERROR: The input file was not found at '{input_csv_path}'",
            file=sys.stderr,
        )
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return

    print(f"\nCheck complete. Results saved to: {output_csv_path}")


def main():
    """
    Parses command-line arguments and runs the URL checker.
    """
    parser = argparse.ArgumentParser(
        description="A script to check a list of relative URLs against a base URL. It records the final destination, status code, and any redirect chains.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "base_url",
        help="The base URL to test against (e.g., 'https://www.example.com').",
    )
    parser.add_argument(
        "input_csv",
        help="Path to the input CSV file. The file should contain one relative URL per row in the first column.",
    )
    parser.add_argument("output_csv", help="Path to write the output CSV report.")

    args = parser.parse_args()

    check_urls(args.base_url, args.input_csv, args.output_csv)


if __name__ == "__main__":
    main()
