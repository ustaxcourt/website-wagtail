"""
This script reads redirects from a CSV file and generates:
- A JSON mapping of redirects (used for inspection/debugging)
- A CloudFront-safe JavaScript file with redirect logic

How to run:
1. Activate your virtual environment
2. From the project root, run:
   python home/utils/create_rules_pdf_redirects.py
"""

import csv
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting redirect generation for CloudFront function...")

    base_dir = Path(__file__).resolve().parent.parent.parent  # points to: website/
    csv_path = base_dir / "home" / "migrations" / "0064_update_rules_documents.csv"
    json_output_path = base_dir / "redirects" / "pdf_redirects.json"
    js_output_path = base_dir / "redirects" / "pdf_redirect_function.js"

    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    js_output_path.parent.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        logger.error(f"CSV file not found at: {csv_path}")
        return

    redirects = {}

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            old_path = f"/files/documents/{row['current_filename'].strip()}"
            new_path = f"/files/documents/{row['new_title'].strip()}"

            if old_path == new_path:
                continue

            redirects[old_path] = new_path

    # Write JSON map
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(redirects, f, indent=2)
    logger.info(f"JSON file generated: {json_output_path}")

    # Write CloudFront Function JS with regex-based logic
    js_code = """
        function handler(event) {
          var request = event.request;

          // Strip /files prefix for uniform matching
          var originalUri = request.uri;
          if (request.uri.startsWith("/files/")) {
            request.uri = request.uri.slice(6);
          }

          var uri = request.uri;

          // Exact path redirects (manual override)
          var redirects = {
            "/documents/Complete_Rules_of_Practice_and_Procedure_Amended_080824.pdf": "/files/documents/Complete-Rules-of-Practice-and-Procedure.pdf",
            "/documents/Rule-229A.pdf": "/files/documents/rule-229A.pdf",
            "/documents/Rule-2302nd-amended.pdf": "/files/documents/rule-230.pdf",
            "/documents/Rule-255.1_amended_08082024.pdf": "/files/documents/rule-255.1.pdf",
            "/documents/Rule-255.2New.pdf": "/files/documents/rule-255.2.pdf",
            "/documents/Rule-255.3New.pdf": "/files/documents/rule-255.3.pdf",
            "/documents/Rule-255.4New.pdf": "/files/documents/rule-255.4.pdf",
            "/documents/Rule-255.5New.pdf": "/files/documents/rule-255.5.pdf",
            "/documents/Rule-255.6New.pdf": "/files/documents/rule-255.6.pdf",
            "/documents/Rule-255.7New.pdf": "/files/documents/rule-255.7.pdf",
            "/documents/Rule-151_1_Amended_03202023.pdf": "/files/documents/rule-151.1.pdf"
          };

          // Avoid infinite redirects if already pointing to final URL
          if (originalUri === redirects[uri]) {
            return request;
          }

          if (redirects[uri] && ("/files" + uri) !== redirects[uri]) {
            return {
              statusCode: 301,
              statusDescription: "Permanent Redirect",
              headers: {
                location: { value: redirects[uri] }
              }
            };
          }

          // Early exit ONLY if the URI is already clean and lowercase
          if (/^\/documents\/rule-[a-z0-9.-]+\.pdf$/.test(uri)) {
            return request;
          }

          // Regex fallback for legacy filenames
          var pattern = /^\/documents\/(Rule-[\dA-Za-z.]+)(?:_?Amended.*|_?amended.*|-?superseded|-?2nd-amended|-?New|-?Oct.*|\.\.)?\.pdf$/i;
          var match = uri.match(pattern);

          if (match) {
            var ruleName = match[1];

            // Normalize name
            ruleName = ruleName.replace(/_/g, "-");
            ruleName = ruleName.replace(/(\d)-(\d[A-Z.]?)/g, "$1.$2");
            ruleName = ruleName.replace(/^Rule/i, "rule");

            var newUri = "/files/documents/" + ruleName + ".pdf";

            // Avoid redirecting to self
            if (originalUri !== newUri) {
              return {
                statusCode: 301,
                statusDescription: "Permanent Redirect",
                headers: {
                  location: { value: newUri }
                }
              };
            }
          }

          return request;
        }
        """

    with open(js_output_path, "w", encoding="utf-8") as f:
        f.write(js_code)

    size_bytes = js_output_path.stat().st_size
    size_kb = round(size_bytes / 1024, 2)
    if size_bytes > 10240:
        logger.warning(f"JS file size is {size_kb} KB (exceeds 10 KB limit)")
    else:
        logger.info(f"JS file generated: {js_output_path} ({size_kb} KB)")
        logger.info(f"{len(redirects)} total redirects processed")


if __name__ == "__main__":
    main()
