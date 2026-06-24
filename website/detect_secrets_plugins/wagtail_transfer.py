import re
from typing import Any, Generator

from detect_secrets.plugins.base import BasePlugin


class WagtailTransferSecretKeyDetector(BasePlugin):
    """Detects hardcoded WAGTAILTRANSFER_SECRET_KEY values."""

    secret_type = "Wagtail Transfer Secret Key"  # pragma: allowlist secret

    # Matches: WAGTAILTRANSFER_SECRET_KEY = "some-value" or 'some-value'
    WAGTAIL_TRANSFER_KEY_PATTERN = re.compile(  # pragma: allowlist secret
        r"""WAGTAILTRANSFER_SECRET_KEY\s*=\s*["']([^"']{8,})["']""",
        re.IGNORECASE,
    )

    def analyze_string(self, line: str, **kwargs: Any) -> Generator[str, None, None]:
        match = self.WAGTAIL_TRANSFER_KEY_PATTERN.search(line)
        if match:
            yield match.group(1)

    def json(self) -> dict[str, Any]:
        return {"name": self.__class__.__name__}
