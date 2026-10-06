"""
CSV import/export for the Question and Answer (FAQ) block on EnhancedStandardPage
and its subclasses (e.g. PetitionerExperiencePage).

The CSV has one row per question with the columns in ``COLUMNS``. Uploads must
include ``question``, ``answer`` and ``filtertag``; ``anchortag`` is optional and is
generated from the question when blank. Downloads always include every column, so a
downloaded file can be edited and uploaded again without changing its anchors.

FilterTags are given by display name (not case-sensitive) and stored as slugs.
Answers are rich text: either plain text (blank lines separate paragraphs) or HTML,
which is passed through the rich text editor's converter so it is limited to the
same features an editor could enter by hand.

Imports never publish. They save a new draft revision of the page, so the change
goes through the normal review workflow and can be reverted from the page history.
"""

import csv
import io
import re

from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.utils.text import slugify
from wagtail import hooks

from home.models.custom_blocks.question_answers import QuestionAnswersBlock
from home.models.snippets.faq_filter_tag import QA_BLOCK_TYPE, FAQFilterTag

COLUMNS = ["question", "answer", "filtertag", "anchortag"]
REQUIRED_COLUMNS = ["question", "answer", "filtertag"]
MAX_ROWS = 500
MAX_GENERATED_ANCHOR_LENGTH = 60

_HTML_TAG = re.compile(r"</?[a-zA-Z][^>]*>")


class FAQCSVError(Exception):
    """The CSV can't be imported. ``errors`` lists every problem found, for display."""

    def __init__(self, errors):
        super().__init__("; ".join(errors))
        self.errors = errors


# Selectors


def faq_sections_list(page):
    """
    The FAQ sections on ``page``'s body as raw block dicts, in page order.

    Includes sections nested in other blocks (e.g. an Anchor Page's body), since each
    is identified by its own block id.
    """
    return list(_find_sections(page.body.get_prep_value()))


def _find_sections(node):
    if isinstance(node, dict):
        if node.get("type") == QA_BLOCK_TYPE and isinstance(node.get("value"), dict):
            yield node
            return
        for value in node.values():
            yield from _find_sections(value)
    elif isinstance(node, list):
        for value in node:
            yield from _find_sections(value)


# Export


def faq_section_to_csv(section):
    """Render a raw FAQ section block dict as CSV text (without a byte order mark)."""
    value = QuestionAnswersBlock().to_python(section["value"])
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(COLUMNS)
    for qa, tag_name in value.entries:
        writer.writerow(
            [qa["question"], qa["answer"].source, tag_name, qa["anchortag"]]
        )
    return output.getvalue()


# Import


def faq_csv_parse(data, *, reserved_anchors=()):
    """
    Parse uploaded CSV bytes into raw question data for ``QuestionAnswersBlock``.

    ``reserved_anchors`` are anchors already used elsewhere on the page; uploaded
    anchors may not reuse them and generated anchors avoid them.

    Every row is checked with the block's own validation before anything is returned,
    so a file with any invalid row raises ``FAQCSVError`` and changes nothing.
    """
    rows = _read_rows(_decode(data))
    errors = []
    tag_slugs = {
        tag.name.casefold(): tag.slug for tag in FAQFilterTag.objects.filter(live=True)
    }
    reserved = set(reserved_anchors)
    given_anchors = {}
    questions = []

    for row_number, row in rows:
        tag_name = row["filtertag"]
        slug = tag_slugs.get(tag_name.casefold())
        if not tag_name:
            errors.append((row_number, "FilterTag is required."))
        elif slug is None:
            errors.append(
                (
                    row_number,
                    f'FilterTag "{tag_name}" does not exist or is not published.',
                )
            )

        anchor = row.get("anchortag", "")
        if anchor:
            if anchor in given_anchors:
                errors.append(
                    (
                        row_number,
                        f'anchortag "{anchor}" is already used on row {given_anchors[anchor]}.',
                    )
                )
            elif anchor in reserved:
                errors.append(
                    (
                        row_number,
                        f'anchortag "{anchor}" is already used by another FAQ section on this page.',
                    )
                )
            given_anchors.setdefault(anchor, row_number)

        questions.append(
            {
                "question": row["question"],
                "answer": _answer_to_rich_text(row["answer"]),
                "anchortag": anchor,
                "filtertag": slug or "",
            }
        )

    used = reserved | set(given_anchors)
    for qa in questions:
        if not qa["anchortag"]:
            qa["anchortag"] = _generate_anchor(qa["question"], used)
            used.add(qa["anchortag"])

    questions_block = QuestionAnswersBlock().child_blocks["questions"]
    try:
        cleaned = questions_block.clean(questions_block.to_python(questions))
    except ValidationError as e:
        errors.extend(_block_errors(e, [number for number, _ in rows]))

    if errors:
        # Stable sort keeps each row's messages in the order they were found
        errors.sort(key=lambda error: error[0])
        raise FAQCSVError([f"Row {row}: {message}" for row, message in errors])
    return questions_block.get_prep_value(cleaned)


def _decode(data):
    # Excel's "CSV UTF-8" adds a byte order mark; its plain "CSV" is Windows-1252
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise FAQCSVError(
        ["The file could not be read. Save it as CSV UTF-8 and try again."]
    )


def _normalize_header(name):
    return re.sub(r"[\s_-]+", "", (name or "").strip().casefold())


def _read_rows(text):
    """Return ``(spreadsheet row number, row dict)`` pairs, skipping blank rows."""
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = next(reader, None)
        if not header or not any(cell.strip() for cell in header):
            raise FAQCSVError(["The file is empty."])

        columns = [_normalize_header(name) for name in header]
        errors = []
        unknown = [name for name, col in zip(header, columns) if col not in COLUMNS]
        if unknown:
            errors.append(
                "Unrecognized column(s): "
                + ", ".join(f'"{name}"' for name in unknown)
                + ". Expected columns: "
                + ", ".join(COLUMNS)
                + "."
            )
        repeated = sorted({col for col in columns if columns.count(col) > 1})
        if repeated:
            errors.append("Repeated column(s): " + ", ".join(repeated) + ".")
        missing = [col for col in REQUIRED_COLUMNS if col not in columns]
        if missing:
            errors.append("Missing required column(s): " + ", ".join(missing) + ".")
        if errors:
            raise FAQCSVError(errors)

        rows = []
        for row_number, cells in enumerate(reader, start=2):
            if not any(cell.strip() for cell in cells):
                continue
            if len(cells) > len(columns):
                errors.append(
                    f"Row {row_number}: has more values than there are columns."
                )
                continue
            cells += [""] * (len(columns) - len(cells))
            rows.append(
                (row_number, {col: cell.strip() for col, cell in zip(columns, cells)})
            )
    except csv.Error as e:
        raise FAQCSVError([f"The file is not a valid CSV: {e}."])

    if errors:
        raise FAQCSVError(errors)
    if not rows:
        raise FAQCSVError(["The file has no questions."])
    if len(rows) > MAX_ROWS:
        raise FAQCSVError(
            [f"The file has {len(rows)} questions; the limit is {MAX_ROWS}."]
        )
    return rows


def _answer_to_rich_text(text):
    """Convert an answer cell to the rich text database format."""
    if not text:
        return ""
    if not _HTML_TAG.search(text):
        paragraphs = re.split(r"\n\s*\n", text.replace("\r\n", "\n"))
        text = "".join(
            "<p>" + escape(p.strip()).replace("\n", "<br/>") + "</p>"
            for p in paragraphs
            if p.strip()
        )
    # Round-trip through the editor widget so the answer only uses enabled features
    widget = (
        QuestionAnswersBlock()
        .child_blocks["questions"]
        .child_block.child_blocks["answer"]
        .field.widget
    )
    return widget.value_from_datadict(
        {"answer": widget.format_value(text)}, {}, "answer"
    )


def _generate_anchor(question, used):
    base = slugify(question)[:MAX_GENERATED_ANCHOR_LENGTH].strip("-") or "question"
    anchor, suffix = base, 2
    while anchor in used:
        anchor = f"{base}-{suffix}"
        suffix += 1
    return anchor


def _block_errors(error, row_numbers):
    """
    Flatten a ListBlockValidationError into ``(row number, message)`` pairs.

    FilterTag errors are skipped: tags are checked by name above, and the block would
    only repeat them as "This field is required."
    """
    errors = []
    for index, item_error in sorted(getattr(error, "block_errors", {}).items()):
        row = row_numbers[index]
        field_errors = getattr(item_error, "block_errors", None)
        if not field_errors:
            errors.extend((row, m) for m in item_error.messages)
            continue
        for field, field_error in field_errors.items():
            if field != "filtertag":
                errors.extend((row, f"{field}: {m}") for m in field_error.messages)
    return errors


# Services


def faq_section_import_csv(
    *, request, page, data, section_id=None, display_filter_section=False
):
    """
    Replace the questions of FAQ section ``section_id`` on ``page`` with those in the
    CSV ``data``, or add a new FAQ section at the end of the body when ``section_id``
    is None. Saves (but does not publish) a new revision and returns it.

    A replaced section keeps its block id and "Display Filter Section" setting.
    Raises ``FAQCSVError`` without saving anything if the CSV is invalid.
    """
    page = page.get_latest_revision_as_object()
    body = page.body.get_prep_value()
    sections = list(_find_sections(body))

    target = None
    if section_id is not None:
        target = next((s for s in sections if s.get("id") == section_id), None)
        if target is None:
            raise FAQCSVError(
                ["That FAQ section is no longer on the page. Reload and try again."]
            )

    reserved = {
        qa["value"].get("anchortag")
        for section in sections
        if section is not target
        for qa in section["value"].get("questions", [])
    }
    questions = faq_csv_parse(data, reserved_anchors=reserved - {None, ""})

    if target is not None:
        target["value"]["questions"] = questions
    else:
        body.append(
            {
                "type": QA_BLOCK_TYPE,
                "value": {
                    "display_filter_section": display_filter_section,
                    "questions": questions,
                },
            }
        )
    page.body = body

    try:
        revision = page.save_revision(user=request.user, log_action=True)
    except ValidationError as e:
        raise FAQCSVError(
            [f"The page could not be saved: {m}" for m in e.messages]
        ) from e

    # Same follow-up as saving a draft in the page editor (e.g. moderation notices)
    for fn in hooks.get_hooks("after_edit_page"):
        fn(request, page)
    return revision
