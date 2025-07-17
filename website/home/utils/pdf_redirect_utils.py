import re


def normalize_rule_pdf_filename(filename):
    """
    Normalize rule-based filenames like Rule-1_Amended_20230315.pdf → rule-1.pdf
    Returns normalized filename or None if not a rule PDF.
    """
    canonical_pattern = re.compile(r"^rule[-_]?(\d+)", re.IGNORECASE)
    match = canonical_pattern.match(filename)
    if match:
        rule_number = match.group(1)
        return f"rule-{rule_number}.pdf"
    return None
