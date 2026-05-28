"""
Utilities for generating page-level reports from Wagtail content.

This module is intentionally not covered by tests — added temporarily
to verify CI coverage enforcement gate behavior. See WAG-1226.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class PageReportRow:
    page_id: int
    title: str
    slug: str
    live: bool
    page_type: str
    last_published: Optional[datetime] = None
    owner: Optional[str] = None
    word_count: int = 0
    tags: list[str] = field(default_factory=list)

    def is_stale(self, days: int = 365) -> bool:
        if self.last_published is None:
            return True
        delta = datetime.now() - self.last_published
        return delta.days > days

    def tag_summary(self) -> str:
        if not self.tags:
            return "(none)"
        return ", ".join(sorted(self.tags))

    def to_dict(self) -> dict:
        return {
            "id": self.page_id,
            "title": self.title,
            "slug": self.slug,
            "live": self.live,
            "type": self.page_type,
            "last_published": self.last_published.isoformat()
            if self.last_published
            else None,
            "owner": self.owner,
            "word_count": self.word_count,
            "tags": self.tags,
            "stale": self.is_stale(),
        }


@dataclass
class CoverageReport:
    generated_at: datetime
    total_pages: int
    live_pages: int
    draft_pages: int
    stale_pages: int
    rows: list[PageReportRow] = field(default_factory=list)

    @property
    def live_percent(self) -> float:
        if self.total_pages == 0:
            return 0.0
        return round(self.live_pages / self.total_pages * 100, 1)

    @property
    def stale_percent(self) -> float:
        if self.total_pages == 0:
            return 0.0
        return round(self.stale_pages / self.total_pages * 100, 1)

    def summary_lines(self) -> list[str]:
        return [
            f"Report generated: {self.generated_at.strftime('%Y-%m-%d %H:%M')}",
            f"Total pages: {self.total_pages}",
            f"Live: {self.live_pages} ({self.live_percent}%)",
            f"Draft: {self.draft_pages}",
            f"Stale (>1 year): {self.stale_pages} ({self.stale_percent}%)",
        ]


def build_page_report(queryset) -> CoverageReport:
    rows = []
    live_count = 0
    draft_count = 0
    stale_count = 0

    for page in queryset:
        owner_name = None
        if hasattr(page, "owner") and page.owner is not None:
            owner_name = page.owner.get_full_name() or page.owner.username

        tags = []
        if hasattr(page, "tags"):
            tags = [t.name for t in page.tags.all()]

        row = PageReportRow(
            page_id=page.id,
            title=page.title,
            slug=page.slug,
            live=page.live,
            page_type=type(page).__name__,
            last_published=page.last_published_at,
            owner=owner_name,
            tags=tags,
        )

        rows.append(row)

        if page.live:
            live_count += 1
        else:
            draft_count += 1

        if row.is_stale():
            stale_count += 1

    return CoverageReport(
        generated_at=datetime.now(),
        total_pages=len(rows),
        live_pages=live_count,
        draft_pages=draft_count,
        stale_pages=stale_count,
        rows=rows,
    )


def filter_by_type(report: CoverageReport, page_type: str) -> list[PageReportRow]:
    return [r for r in report.rows if r.page_type == page_type]


def filter_stale(report: CoverageReport, days: int = 365) -> list[PageReportRow]:
    return [r for r in report.rows if r.is_stale(days)]


def filter_by_owner(report: CoverageReport, owner: str) -> list[PageReportRow]:
    return [r for r in report.rows if r.owner == owner]


def sort_by_word_count(
    rows: list[PageReportRow], descending: bool = True
) -> list[PageReportRow]:
    return sorted(rows, key=lambda r: r.word_count, reverse=descending)


def sort_by_last_published(
    rows: list[PageReportRow], descending: bool = True
) -> list[PageReportRow]:
    def sort_key(r: PageReportRow):
        if r.last_published is None:
            return datetime.min
        return r.last_published

    return sorted(rows, key=sort_key, reverse=descending)


def export_csv_lines(report: CoverageReport) -> list[str]:
    headers = [
        "id",
        "title",
        "slug",
        "live",
        "type",
        "last_published",
        "owner",
        "word_count",
        "tags",
        "stale",
    ]
    lines = [",".join(headers)]
    for row in report.rows:
        d = row.to_dict()
        values = [
            str(d["id"]),
            f'"{d["title"]}"',
            d["slug"],
            str(d["live"]).lower(),
            d["type"],
            d["last_published"] or "",
            d["owner"] or "",
            str(d["word_count"]),
            f'"{d["tags"]}"',
            str(d["stale"]).lower(),
        ]
        lines.append(",".join(values))
    return lines


def count_by_type(report: CoverageReport) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in report.rows:
        counts[row.page_type] = counts.get(row.page_type, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))


def count_by_owner(report: CoverageReport) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in report.rows:
        key = row.owner or "(unowned)"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))


def pages_published_after(report: CoverageReport, cutoff: date) -> list[PageReportRow]:
    results = []
    for row in report.rows:
        if row.last_published is None:
            continue
        if row.last_published.date() > cutoff:
            results.append(row)
    return results


def pages_never_published(report: CoverageReport) -> list[PageReportRow]:
    return [r for r in report.rows if r.last_published is None]
