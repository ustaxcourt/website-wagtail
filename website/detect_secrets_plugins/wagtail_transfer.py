import re
from typing import IO, Any, Generator

from detect_secrets.plugins.base import BasePlugin


class WagtailTransferSecretKeyDetector(BasePlugin):
    """Detects hardcoded WAGTAILTRANSFER_SECRET_KEY values."""

    secret_type = "Wagtail Transfer Secret Key"  # pragma: allowlist secret

    # Matches: WAGTAILTRANSFER_SECRET_KEY = "some-value" or 'some-value'  # pragma: allowlist secret
    WAGTAIL_TRANSFER_KEY_PATTERN = re.compile(  # pragma: allowlist secret
        r"""WAGTAILTRANSFER_SECRET_KEY\s*=\s*["']([^"']{8,})["']""",
        re.IGNORECASE,
    )

    # Triple-quoted assignment — used by analyze_file for multi-line spans.
    _TRIPLE_QUOTE = re.compile(  # pragma: allowlist secret
        r'WAGTAILTRANSFER_SECRET_KEY\s*=\s*(?:"""(.*?)"""|\'\'\'(.*?)\'\'\')',
        re.DOTALL | re.IGNORECASE,
    )

    def analyze_string(self, line: str, **kwargs: Any) -> Generator[str, None, None]:
        for match in self.WAGTAIL_TRANSFER_KEY_PATTERN.finditer(line):
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

        # Triple-quoted strings that span more than one line.
        content = "".join(lines)
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

    def json(self) -> dict[str, Any]:
        return {"name": self.__class__.__name__}
