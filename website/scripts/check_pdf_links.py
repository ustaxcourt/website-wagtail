#!/usr/bin/env python3
"""
PDF Link Checker for ustaxcourt.gov

Crawls the site to find all PDFs, downloads them, extracts embedded hyperlinks
(via PyMuPDF), and verifies that any links pointing back to the site are valid.

Usage:
    python scripts/check_pdf_links.py
    python scripts/check_pdf_links.py --host qa-web.ustaxcourt.gov
    python scripts/check_pdf_links.py --use-manifest
    python scripts/check_pdf_links.py --output-dir /some/other/path

Requirements:
    pip install -r requirements/utilities.txt
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse
import concurrent.futures
import threading

try:
    import fitz  # PyMuPDF
except ImportError:
    print(
        "ERROR: PyMuPDF is required.\n  pip install -r requirements/utilities.txt",
        file=sys.stderr,
    )
    sys.exit(1)

import requests
from bs4 import BeautifulSoup


USTAXCOURT_DOMAIN = "ustaxcourt.gov"
DEFAULT_HOST = "www." + USTAXCOURT_DOMAIN

_SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = _SCRIPT_DIR.parent / "tmp" / "pdf_link_check"


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------


def _normalize(url: str) -> str:
    """Strip fragment and trailing slash for deduplication."""
    p = urlparse(url)
    path = p.path.rstrip("/") or "/"
    return urlunparse(p._replace(path=path, fragment=""))


def _is_ustaxcourt(url: str) -> bool:
    return urlparse(url).netloc.endswith(USTAXCOURT_DOMAIN)


def _swap_host(url: str, target_host: str) -> str:
    """Replace the subdomain of any ustaxcourt.gov URL with target_host."""
    p = urlparse(url)
    if p.netloc and p.netloc.endswith(USTAXCOURT_DOMAIN):
        return urlunparse(p._replace(netloc=target_host))
    return url


def _make_session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = "ustaxcourt-pdf-link-checker/1.0"
    return s


# ---------------------------------------------------------------------------
# Crawl phase
# ---------------------------------------------------------------------------


def crawl_site(host: str, session: requests.Session) -> dict[str, list[str]]:
    """
    Spider the site and collect all PDF links with the pages they appear on.
    Returns {pdf_url: [source_page_url, ...]}
    """
    start = f"https://{host}/"
    visited: set[str] = set()
    queue: set[str] = {start}
    pdf_sources: dict[str, list[str]] = defaultdict(list)
    count = 0

    print(f"Crawling {start} ...")

    while queue:
        url = queue.pop()
        key = _normalize(url)
        if key in visited:
            continue
        visited.add(key)
        count += 1

        try:
            resp = session.get(url, timeout=15)
        except requests.RequestException:
            continue

        if resp.status_code != 200:
            continue
        if "html" not in resp.headers.get("content-type", ""):
            continue

        print(
            f"  [{count}] {url} — {len(pdf_sources)} PDFs so far", end="\r", flush=True
        )

        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("mailto:", "tel:", "#", "javascript:")):
                continue
            full = urljoin(url, href)
            p = urlparse(full)
            if p.scheme not in ("http", "https"):
                continue

            if _is_ustaxcourt(full) and p.path.lower().endswith(".pdf"):
                if url not in pdf_sources[full]:
                    pdf_sources[full].append(url)
            elif p.netloc == host and not p.path.lower().endswith(".pdf"):
                if _normalize(full) not in visited:
                    queue.add(full)

    print(
        f"\nCrawl complete: {count} pages visited, {len(pdf_sources)} unique PDFs found."
    )
    return dict(pdf_sources)


# ---------------------------------------------------------------------------
# Manifest phase
# ---------------------------------------------------------------------------


def _head_size(url: str, session: requests.Session) -> int:
    try:
        r = session.head(url, timeout=10, allow_redirects=True)
        cl = r.headers.get("content-length")
        return int(cl) if cl else -1
    except Exception:
        return -1


def build_manifest(
    pdf_sources: dict[str, list[str]],
    session: requests.Session,
    manifest_path: Path,
    host: str,
) -> list[dict]:
    print(f"Fetching file sizes for {len(pdf_sources)} PDFs...")
    size_map: dict[str, int] = {}
    done = 0
    lock = threading.Lock()

    def fetch_size(url: str) -> None:
        nonlocal done
        sz = _head_size(url, session)
        with lock:
            size_map[url] = sz
            done += 1
            print(f"  {done}/{len(pdf_sources)} sizes fetched", end="\r", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        list(ex.map(fetch_size, pdf_sources))
    print()

    entries = sorted(
        [
            {
                "url": url,
                "found_on": sources,
                "size_bytes": size_map.get(url, -1),
            }
            for url, sources in pdf_sources.items()
        ],
        key=lambda e: e["url"],
    )

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "host": host,
        "count": len(entries),
        "pdfs": entries,
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Manifest saved: {manifest_path}")
    return entries


def load_manifest(manifest_path: Path) -> list[dict]:
    data = json.loads(manifest_path.read_text())
    print(f"Loaded manifest: {data['count']} PDFs (generated {data['generated_at']})")
    return data["pdfs"]


# ---------------------------------------------------------------------------
# Download phase
# ---------------------------------------------------------------------------


def _download_one(
    entry: dict, download_dir: Path, session: requests.Session
) -> tuple[dict, Path | None]:
    url = entry["url"]
    name = Path(urlparse(url).path).name or "unknown.pdf"
    dest = download_dir / name
    if dest.exists() and dest.stat().st_size > 0:
        return entry, dest
    try:
        r = session.get(url, timeout=60, stream=True)
        if r.status_code == 200:
            dest.write_bytes(r.content)
            return entry, dest
        return entry, None
    except Exception:
        return entry, None


def download_pdfs(
    entries: list[dict], download_dir: Path, session: requests.Session
) -> list[tuple[dict, Path | None]]:
    download_dir.mkdir(parents=True, exist_ok=True)
    results: list[tuple[dict, Path | None]] = []
    lock = threading.Lock()
    done = 0

    def dl(entry: dict) -> None:
        nonlocal done
        result = _download_one(entry, download_dir, session)
        with lock:
            results.append(result)
            done += 1
            ok = sum(1 for _, p in results if p)
            print(f"  {done}/{len(entries)} processed ({ok} ok)", end="\r", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        list(ex.map(dl, entries))
    print()
    return results


# ---------------------------------------------------------------------------
# Link extraction phase
# ---------------------------------------------------------------------------


def extract_pdf_links(pdf_path: Path) -> list[str]:
    """Return all HTTP(S) hyperlink URIs embedded in a PDF."""
    links: list[str] = []
    try:
        with fitz.open(str(pdf_path)) as doc:
            for page in doc:
                for link in page.get_links():
                    uri = link.get("uri", "")
                    if uri.startswith(("http://", "https://")):
                        links.append(uri)
    except Exception:
        pass
    return links


# ---------------------------------------------------------------------------
# Link-check phase
# ---------------------------------------------------------------------------


def _check_one(url: str, session: requests.Session) -> int:
    try:
        r = session.head(url, timeout=15, allow_redirects=True)
        if r.status_code == 405:
            r = session.get(url, timeout=15, stream=True)
        return r.status_code
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def _generate_report(
    broken: dict[str, dict],
    report_path: Path,
    host: str,
    stats: dict,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "PDF LINK CHECKER REPORT",
        "=" * 70,
        f"Generated:         {now}",
        f"Target host:       {host}",
        f"PDFs analyzed:     {stats['pdfs_checked']}",
        f"PDFs with links:   {stats['pdfs_with_links']}",
        f"Total links found: {stats['links_found']}",
        f"Unique links:      {stats['unique_links']}",
        f"Broken links:      {len(broken)}",
        "",
    ]

    if not broken:
        lines.append("All links are valid. No broken links found.")
    else:
        lines.append(f"BROKEN LINKS ({len(broken)})")
        lines.append("=" * 70)
        for checked_url, info in sorted(broken.items()):
            lines += [
                "",
                f"  URL:    {checked_url}",
                f"  Status: {info['status'] or 'connection error'}",
                "  Found in:",
            ]
            for item in info["pdfs"]:
                lines.append(f"    PDF:  {item['pdf_url']}")
                for pg in item["found_on"]:
                    lines.append(f"          (site page: {pg})")

    text = "\n".join(lines) + "\n"
    report_path.write_text(text)
    print("\n" + text)
    print(f"Report saved: {report_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crawl ustaxcourt.gov, download PDFs, and verify embedded links.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        metavar="HOSTNAME",
        help=f"Site to crawl and check links against (default: {DEFAULT_HOST})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        metavar="DIR",
        help=f"Directory for downloads, manifest, and report (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--use-manifest",
        action="store_true",
        help="Skip crawling and use an existing manifest.json in --output-dir. "
        "Errors if the manifest does not exist.",
    )
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    manifest_path = output_dir / "manifest.json"
    download_dir = output_dir / "downloads"
    report_path = output_dir / "report.txt"

    session = _make_session()

    # ---- Manifest ----
    if args.use_manifest:
        if not manifest_path.exists():
            print(
                f"ERROR: --use-manifest specified but no manifest found at:\n  {manifest_path}",
                file=sys.stderr,
            )
            sys.exit(1)
        entries = load_manifest(manifest_path)
    else:
        pdf_sources = crawl_site(args.host, session)
        entries = build_manifest(pdf_sources, session, manifest_path, args.host)

    # ---- Summary + prompt ----
    known = [e for e in entries if e["size_bytes"] > 0]
    total_mb = sum(e["size_bytes"] for e in known) / (1024 * 1024)

    print(f"\n{'─' * 50}")
    print(f"  PDFs found:  {len(entries)}")
    if known:
        coverage = f"{len(known)}/{len(entries)}"
        print(f"  Total size:  ~{total_mb:.1f} MB ({coverage} files with known sizes)")
    else:
        print("  Total size:  unknown (server did not return Content-Length)")
    print(f"  Output dir:  {output_dir}")
    print(f"{'─' * 50}")

    answer = input("\nProceed with download and analysis? [y/N] ").strip().lower()
    if answer not in ("y", "yes"):
        print("Aborted. Manifest has been saved.")
        sys.exit(0)

    # ---- Download ----
    print(f"\nDownloading PDFs to {download_dir} ...")
    downloaded = download_pdfs(entries, download_dir, session)
    ok_pairs = [(e, p) for e, p in downloaded if p]
    failed = [(e, p) for e, p in downloaded if not p]
    print(f"  {len(ok_pairs)} ok, {len(failed)} failed.")
    for e, _ in failed:
        print(f"  FAILED: {e['url']}")

    # ---- Extract links ----
    print("\nExtracting links from PDFs...")
    # checked_url → list of {pdf_url, found_on}
    link_index: dict[str, list[dict]] = defaultdict(list)
    pdfs_with_links = 0
    total_links = 0

    for entry, pdf_path in ok_pairs:
        raw = extract_pdf_links(pdf_path)
        site_links = [link for link in raw if _is_ustaxcourt(link)]
        if not site_links:
            continue
        pdfs_with_links += 1
        total_links += len(site_links)
        for link in site_links:
            checked_url = _swap_host(link, args.host)
            link_index[checked_url].append(
                {"pdf_url": entry["url"], "found_on": entry["found_on"]}
            )

    unique_links = len(link_index)
    print(
        f"  {total_links} links found ({unique_links} unique) "
        f"across {pdfs_with_links} PDFs."
    )

    # ---- Check links ----
    print(f"\nChecking {unique_links} unique links...")
    broken: dict[str, dict] = {}
    done = 0
    lock = threading.Lock()

    def check_and_record(url: str) -> None:
        nonlocal done
        code = _check_one(url, session)
        with lock:
            done += 1
            print(f"  {done}/{unique_links} checked", end="\r", flush=True)
            if code not in (200, 301, 302, 303, 307, 308):
                broken[url] = {"status": code, "pdfs": link_index[url]}

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        list(ex.map(check_and_record, link_index))
    print()

    # ---- Report ----
    _generate_report(
        broken,
        report_path,
        host=args.host,
        stats={
            "pdfs_checked": len(ok_pairs),
            "pdfs_with_links": pdfs_with_links,
            "links_found": total_links,
            "unique_links": unique_links,
        },
    )


if __name__ == "__main__":
    main()
