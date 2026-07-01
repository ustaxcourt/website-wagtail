import re
from typing import Any, Generator

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
    """

    secret_type = "Broad Secret Keyword"  # pragma: allowlist secret

    # Matches UPPERCASE_PREFIX_KEY patterns:
    # - Optional UPPERCASE segments ending in underscore (e.g. API_, ACCESS_)
    # - Followed by one of the target keywords in UPPERCASE
    # - Assigned a quoted value of at least 8 characters
    # No IGNORECASE flag so lowercase variable names do not match.
    PATTERN = re.compile(  # pragma: allowlist secret
        r"(?<![a-zA-Z])"
        r"(?:[A-Z0-9]+_)*"
        r"(?:KEY|TOKEN|AUTH|CREDENTIAL|CREDENTIALS|OAUTH|SIGNATURE)"
        r"\s*=\s*"
        r'["\']([^"\']{8,})["\']',
    )

    def analyze_string(self, line: str, **kwargs: Any) -> Generator[str, None, None]:
        for match in self.PATTERN.finditer(line):
            yield match.group(1)

    def json(self) -> dict[str, Any]:
        return {"name": self.__class__.__name__}
