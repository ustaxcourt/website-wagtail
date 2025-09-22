# URL Redirect and Status Checker

This Python script checks a list of relative URLs from a CSV file against a specified base URL. It follows any redirects, records the final destination URL and HTTP status code, and logs the entire redirect chain. This is useful for SEO audits, website migrations, or cleaning up broken links.

## Prerequisites

Python 3.6+
The requests library

You can install the necessary library using pip:

pip install requests
 

## How to Use

### Prepare your CSV file:
Create a CSV file (e.g., urls_to_check.csv) with a single column containing the relative URLs you want to check. Each URL path should be on a new row.

### Run the script from your terminal:
Execute the url_checker.py script, providing the base URL, the path to your input CSV, and the desired path for the output report.

Example Command: `python url_checker.py "https://dev-web.ustaxcourt.gov" "paths_for_validation.csv" "results.csv"`

### Review the results:
The script will create an output CSV file (e.g., results.csv) with the following columns:

- Result: An emoji for a quick visual status check (✅ for success, ❌ for not found, etc.).
- Final Status Code: The HTTP status code of the final destination (e.g., 200 for success, 404 for not found).
- Original Relative URL: The path from your input file.
- Full URL Checked: The full URL that the script tested (base_url + relative_url).
- Final Destination URL: The URL of the page after all redirects.
- Redirect Chain: A visual representation of the redirect path, showing each URL and its status code.

## Example Output

Result,Final Status Code,Original Relative URL,Full URL Checked,Final Destination URL,Redirect Chain
✅,200,/about-us,https://www.google.com/search?q=https://www.google.com/about-us,https://about.google/,https://www.google.com/search?q=https://www.google.com/about-us (301) -> https://about.google/ (200)
❌,404,/non-existent-page,https://www.google.com/search?q=https://www.google.com/non-ex..,https://www.google.com/search?q=https://www.google.com/non-ex...,No redirects
❗,N/A,/bad-domain,https://www.nonexistent...,Error,Max retries exceeded with url...
 