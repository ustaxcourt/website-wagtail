#!/bin/bash

# A script to scan pages from a sitemap and list all hyperlinks found on each page.
#
# Usage:
# 1. Save the sitemap content you provided to a file named 'sitemap.xml' in the same directory as this script.
# 2. Save this script as 'check_links.sh'.
# 3. Open your terminal and make the script executable: chmod +x check_links.sh
# 4. Run the script: ./check_links.sh
# 5. Optional: To save the output to a file, run: ./check_links.sh > found_links.txt

# --- Configuration ---
SITEMAP_FILE="sitemap.xml"
# The domain to check against. This helps filter out irrelevant links if needed,
# but for now, we will list all of them.
TARGET_DOMAIN="ustaxcourt.gov"

# --- Script Body ---

# Check if the sitemap file exists
if [ ! -f "$SITEMAP_FILE" ]; then
    echo "Error: Sitemap file not found at '$SITEMAP_FILE'"
    echo "Please save your sitemap content to a file named 'sitemap.xml' in this directory."
    exit 1
fi

echo "Starting hyperlink scan using sitemap: $SITEMAP_FILE"
echo "----------------------------------------------------"

# Extract all <loc> URLs from the sitemap.xml file.
# We use xmllint for reliable XML parsing.
# The XPath is updated to use local-name() to correctly handle the default XML namespace
# found in most sitemap files (e.g., xmlns="http://www.sitemaps.org/schemas/sitemap/0.9").
# This prevents the "XPath set is empty" error.
xmllint --xpath "//*[local-name()='url']/*[local-name()='loc']/text()" "$SITEMAP_FILE" | while read page_url; do

    # Print the page we are currently scanning
    echo ""
    echo "Scanning Page: $page_url"

    # Fetch the HTML content of the page, follow redirects (-L), and stay silent (-s).
    # Then, extract all href attributes from <a> tags.
    #
    # - grep -Eo '<a [^>]*href="[^"]+"': Finds all instances of <a ... href="...">, printing only the match.
    # - awk -F'href="' '{print $2}': Splits the result by 'href="' and prints the part after it.
    # - awk -F'"' '{print $1}': Splits the result by '"' and prints the part before it (the URL).
    # - grep -v -E '(^#|javascript:void|mailto:)' : Filters out anchor links, javascript calls, and mailto links.
    # - sort -u: Sorts the links and removes duplicates for a clean list.
    found_links=$(curl -sL "$page_url" | grep -Eo '<a [^>]*href="[^"]+"' | awk -F'href="' '{print $2}' | awk -F'"' '{print $1}' | grep -v -E '(^#|javascript:void|mailto:)' | sort -u)

    if [ -z "$found_links" ]; then
        echo "  -> No relevant hyperlinks found."
    else
        # Print each found link for the current page
        echo "$found_links" | while read link; do
            echo "  -> Found Link: $link"
        done
    fi

    # Be polite and wait for half a second before hitting the next page.
    sleep 0.5
done

echo "----------------------------------------------------"
echo "Scan complete."
