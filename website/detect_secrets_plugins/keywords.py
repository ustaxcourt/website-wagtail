import re
from typing import IO, Any, Generator

from detect_secrets.plugins.base import BasePlugin


class BroadKeywordDetector(BasePlugin):
    """
    Catches hardcoded secrets assigned to variable names that detect-secrets
    v1.5.0's built-in KeywordDetector misses.

    The built-in detector only catches compound patterns (api_key, auth_key,
    private_key) and full words (secret, password). It misses standalone
    uppercase constants like KEY, TOKEN, AUTH, CREDENTIAL and compound forms
    ending in TOKEN (e.g. API_TOKEN, ACCESS_TOKEN).

    This plugin targets Python/Django settings-style UPPERCASE constants only.
    Lowercase variable names (e.g. test_key, auth_token as parameters) are
    intentionally excluded to avoid false positives.

    Multi-line detection:
    - Triple-quoted strings: KEY = \"""...\"""  (may span lines)
    - Parenthesized implicit concatenation: KEY = (\\n    "part1"\\n    "part2"\\n)
    """

    secret_type = "Broad Secret Keyword"  # pragma: allowlist secret

    # Single-line: KEYWORD = "value" or 'value' (>= 8 chars, case-sensitive)
    PATTERN = re.compile(  # pragma: allowlist secret
        r"(?<![a-zA-Z])"
        r"(?:[A-Z0-9]+_)*"
        r"(?:KEY|TOKEN|AUTH|CREDENTIAL|CREDENTIALS|OAUTH|SIGNATURE)"
        r"\s*=\s*"
        r'["\']([^"\']{8,})["\']',
    )

    # Triple-quoted assignment — used by analyze_file for multi-line spans.
    _TRIPLE_QUOTE = re.compile(  # pragma: allowlist secret
        r"(?<![a-zA-Z])"
        r"(?:[A-Z0-9]+_)*"
        r"(?:KEY|TOKEN|AUTH|CREDENTIAL|CREDENTIALS|OAUTH|SIGNATURE)"
        r"\s*=\s*"
        r'(?:"""(.*?)"""|\'\'\'(.*?)\'\'\')',
        re.DOTALL,
    )

    # Parenthesized implicit string concatenation across lines.
    _PAREN_CONCAT = re.compile(  # pragma: allowlist secret
        r"(?<![a-zA-Z])"
        r"(?:[A-Z0-9]+_)*"
        r"(?:KEY|TOKEN|AUTH|CREDENTIAL|CREDENTIALS|OAUTH|SIGNATURE)"
        r"\s*=\s*"
        r'\(\s*((?:["\'][^"\']*["\'][\s\\]*)+)\s*\)',
        re.DOTALL,
    )

    _STRING_PARTS = re.compile(r'["\']([^"\']*)["\']')

    def analyze_string(self, line: str, **kwargs: Any) -> Generator[str, None, None]:
        for match in self.PATTERN.finditer(line):
            yield match.group(1)

    def analyze_file(self, f: IO) -> Generator[Any, None, None]:
        from detect_secrets.core.potential_secret import PotentialSecret

        lines = f.readlines()

        # Per-line analysis via analyze_line so # pragma: allowlist secret is honoured.
        for line_number, line in enumerate(lines, start=1):
            yield from self.analyze_line(
                filename=f.name,
                line=line,
                line_number=line_number,
            )

        content = "".join(lines)

        # Triple-quoted strings that span more than one line.
        for match in self._TRIPLE_QUOTE.finditer(content):
            if "\n" not in match.group(0):
                continue  # Single-line triple-quoted; already caught above.
            secret = next(g for g in match.groups() if g is not None).strip()
            if len(secret) < 8:
                continue
            line_number = content[: match.start()].count("\n") + 1
            yield PotentialSecret(
                type=self.secret_type,
                filename=f.name,
                secret=secret,
                line_number=line_number,
            )

        # Parenthesized implicit concatenation that spans more than one line.
        for match in self._PAREN_CONCAT.finditer(content):
            if "\n" not in match.group(0):
                continue  # Single-line paren; already caught above.
            parts = self._STRING_PARTS.findall(match.group(1))
            secret = "".join(parts)
            if len(secret) < 8:
                continue
            line_number = content[: match.start()].count("\n") + 1
            yield PotentialSecret(
                type=self.secret_type,
                filename=f.name,
                secret=secret,
                line_number=line_number,
            )

    def json(self) -> dict[str, Any]:
        return {"name": self.__class__.__name__}
