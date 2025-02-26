import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import List


@dataclass
class Link:
    title: str
    url: str
    filename: str


@dataclass
class Section:
    heading: str
    links: List[Link]


def download_pdf(url: str, output_dir: str, filename: str) -> None:
    """Download a PDF file from the given URL"""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download: {url}")


def extract_sections(url: str) -> List[Section]:
    """Extract sections and their links from the webpage"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    sections = []

    # Find all container divs that contain headers and links
    containers = soup.find_all("div", class_="stacks_out")

    for container in containers:
        # Find the header
        header = container.find("h3")
        if not header:
            continue

        # Find the list of links
        link_list = container.find("ul", class_="nav")
        if not link_list:
            continue

        links = []
        for link in link_list.find_all("a"):
            href = link.get("href")
            if href and href.endswith(".pdf"):
                filename = os.path.basename(href)
                links.append(
                    Link(
                        title=link.text.strip(),
                        url=urljoin(url, href),
                        filename=filename,
                    )
                )

        if links:
            sections.append(Section(heading=header.text.strip(), links=links))

    return sections


def generate_json_structure(sections: List[Section]) -> List[dict]:
    """Generate JSON structure for the sections and links"""
    json_structure = []

    for section in sections:
        # Add heading
        json_structure.append({"type": "h2", "value": section.heading})

        # Add links
        json_structure.append(
            {
                "type": "links",
                "value": {
                    "links": [
                        {
                            "title": link.title,
                            "icon": "PDF",  # You might want to adjust this
                            "document": link.filename,
                            "url": None,
                        }
                        for link in section.links
                    ]
                },
            }
        )

    return json_structure


def main():
    # Configuration
    url = "https://www.ustaxcourt.gov/rules.html"  # Replace with actual URL
    output_dir = "downloaded_pdfs"

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Extract sections and download PDFs
    sections = extract_sections(url)

    # Download all PDFs
    for section in sections:
        for link in section.links:
            download_pdf(link.url, output_dir, link.filename)

    # Generate JSON structure
    json_structure = generate_json_structure(sections)

    # Save JSON structure
    with open(os.path.join(output_dir, "structure.json"), "w") as f:
        json.dump(json_structure, f, indent=4)


if __name__ == "__main__":
    main()
