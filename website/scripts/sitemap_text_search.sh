#!/usr/bin/env bash
# Search all pages in sitemap.xml for a given text string

# --- Input validation ---
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <sitemap_url_or_file> <search_text>"
    exit 1
fi

SITEMAP="$1"
SEARCH_TEXT="$2"

# --- Check dependencies ---
for cmd in curl xmllint grep; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: '$cmd' is required but not installed."
        exit 1
    fi
done

# --- Get sitemap content ---
if [[ "$SITEMAP" =~ ^https?:// ]]; then
    echo "Downloading sitemap from $SITEMAP..."
    SITEMAP_CONTENT=$(curl -s "$SITEMAP")
    if [[ -z "$SITEMAP_CONTENT" ]]; then
        echo "Error: Failed to download sitemap."
        exit 1
    fi
else
    if [[ ! -f "$SITEMAP" ]]; then
        echo "Error: File '$SITEMAP' not found."
        exit 1
    fi
    SITEMAP_CONTENT=$(cat "$SITEMAP")
fi

# --- Extract URLs from sitemap ---
URLS=$(echo "$SITEMAP_CONTENT" | xmllint --xpath "//*[local-name()='loc']/text()" - 2>/dev/null)
if [[ -z "$URLS" ]]; then
    echo "Error: No URLs found in sitemap."
    exit 1
fi

# --- Search each page ---
echo "Searching for '$SEARCH_TEXT' in pages..."
while IFS= read -r url; do
    echo "Checking: $url"
    PAGE_CONTENT=$(curl -s "$url")

    # pos=$(echo "$PAGE_CONTENT" | awk -v w="<footer id=" '{
    #     split($0, arr, " ")
    #     for (i in arr) if (arr[i] == w) {
    #         print i-1
    #         exit
    #     }
    # }')
    # PAGE_CONTENT="${PAGE_CONTENT:0:$pos}"

    if echo "$PAGE_CONTENT" | grep -Fqi "$SEARCH_TEXT"; then
        echo "MATCH FOUND: $url"
    fi
done <<< "$URLS"

echo "Search complete."
