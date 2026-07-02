import re
from typing import Any, Generator, Optional

from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets.plugins.base import BasePlugin
from detect_secrets.util.code_snippet import CodeSnippet

_KEYWORD = r"(?:[A-Z0-9]+_)*(?:KEY|TOKEN|AUTH|CREDENTIAL|CREDENTIALS|OAUTH|SIGNATURE)"

_STRING_PARTS = re.compile(r'["\']([^"\']*)["\']')


def _extract_quoted(match: "re.Match") -> Optional[str]:
    return next((g for g in match.groups() if g is not None), None)


def _extract_paren_concat(match: "re.Match") -> Optional[str]:
    return "".join(_STRING_PARTS.findall(match.group(1)))


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

    NOTE ON MULTI-LINE DETECTION: detect-secrets' scan pipeline
    (scan_file/scan_diff) only ever calls `analyze_line`, one physical line
    at a time - there is no "whole file" hook a plugin can implement. The
    only cross-line information available is the `context` (CodeSnippet)
    argument `analyze_line` optionally receives: a window of a few lines
    before/after the current one. `analyze_line` below uses that window to
    catch secrets split across lines, reporting a match only on the call
    whose `line_number` is the line the match starts on (so it isn't
    reported once per overlapping line). This logic is intentionally
    duplicated in wagtail_transfer.py rather than shared, because
    detect-secrets loads each `--plugin <file>` in isolation via
    importlib (see `import_file_as_module`), without adding this
    directory to `sys.path` - a cross-file import here would only work
    by accident (e.g. under pytest, which happens to put `website/` on
    `sys.path`) and would break the real pre-commit hook.
    """

    secret_type = "Broad Secret Keyword"  # pragma: allowlist secret
    min_secret_length = 8

    # Single-line: KEYWORD = "value" or 'value' (>= 8 chars, case-sensitive)
    PATTERN = re.compile(  # pragma: allowlist secret
        rf"(?<![a-zA-Z]){_KEYWORD}\s*=\s*" r'["\']([^"\']{8,})["\']',
    )

    # Triple-quoted assignment, possibly spanning multiple lines.
    _TRIPLE_QUOTE = re.compile(  # pragma: allowlist secret
        rf'(?<![a-zA-Z]){_KEYWORD}\s*=\s*(?:"""(.*?)"""|\'\'\'(.*?)\'\'\')',
        re.DOTALL,
    )

    # Parenthesized implicit string concatenation, possibly spanning multiple lines.
    _PAREN_CONCAT = re.compile(  # pragma: allowlist secret
        rf'(?<![a-zA-Z]){_KEYWORD}\s*=\s*\(\s*((?:["\'][^"\']*["\'][\s\\]*)+)\s*\)',
        re.DOTALL,
    )

    multiline_patterns = (
        (_TRIPLE_QUOTE, _extract_quoted),
        (_PAREN_CONCAT, _extract_paren_concat),
    )

    def analyze_string(self, line: str, **kwargs: Any) -> Generator[str, None, None]:
        for match in self.PATTERN.finditer(line):
            yield match.group(1)

    def analyze_line(
        self,
        filename: str,
        line: str,
        line_number: int = 0,
        context: Optional[CodeSnippet] = None,
        **kwargs: Any,
    ) -> set:
        output = super().analyze_line(
            filename=filename,
            line=line,
            line_number=line_number,
            context=context,  # type: ignore[arg-type]  # BasePlugin's stub omits Optional
            **kwargs,
        )

        if context is not None:
            content = "".join(context.lines)
            for pattern, extract in self.multiline_patterns:
                for match in pattern.finditer(content):
                    if "\n" not in match.group(0):
                        continue  # Single-line match; analyze_string already covers this.

                    match_line_number = (
                        context.start_line + 1 + content[: match.start()].count("\n")
                    )
                    if match_line_number != line_number:
                        continue  # Only report once, on the call for the starting line.

                    secret = extract(match)
                    if secret is None:
                        continue
                    secret = secret.strip()
                    if len(secret) < self.min_secret_length:
                        continue

                    output.add(
                        PotentialSecret(
                            type=self.secret_type,
                            filename=filename,
                            secret=secret,
                            line_number=line_number,
                        ),
                    )

        return output

    def json(self) -> dict[str, Any]:
        return {"name": self.__class__.__name__}
