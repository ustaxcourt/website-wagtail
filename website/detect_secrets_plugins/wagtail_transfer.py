import re
from typing import Any, Generator, Optional

from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets.plugins.base import BasePlugin
from detect_secrets.util.code_snippet import CodeSnippet


def _extract_quoted(match: "re.Match") -> Optional[str]:
    return next((g for g in match.groups() if g is not None), None)


class WagtailTransferSecretKeyDetector(BasePlugin):
    """Detects hardcoded WAGTAILTRANSFER_SECRET_KEY values.

    NOTE ON MULTI-LINE DETECTION: detect-secrets' scan pipeline
    (scan_file/scan_diff) only ever calls `analyze_line`, one physical line
    at a time - there is no "whole file" hook a plugin can implement. The
    only cross-line information available is the `context` (CodeSnippet)
    argument `analyze_line` optionally receives: a window of a few lines
    before/after the current one. `analyze_line` below uses that window to
    catch secrets split across lines (e.g. triple-quoted strings), reporting
    a match only on the call whose `line_number` is the line the match
    starts on (so it isn't reported once per overlapping line). This logic
    is intentionally duplicated in keywords.py rather than shared, because
    detect-secrets loads each `--plugin <file>` in isolation via importlib
    (see `import_file_as_module`), without adding this directory to
    `sys.path` - a cross-file import here would only work by accident (e.g.
    under pytest, which happens to put `website/` on `sys.path`) and would
    break the real pre-commit hook.
    """

    secret_type = "Wagtail Transfer Secret Key"  # pragma: allowlist secret
    min_secret_length = 8

    # Matches: WAGTAILTRANSFER_SECRET_KEY = "some-value" or 'some-value'  # pragma: allowlist secret
    WAGTAIL_TRANSFER_KEY_PATTERN = re.compile(  # pragma: allowlist secret
        r"""WAGTAILTRANSFER_SECRET_KEY\s*=\s*["']([^"']{8,})["']""",
        re.IGNORECASE,
    )

    # Triple-quoted assignment, possibly spanning multiple lines.
    _TRIPLE_QUOTE = re.compile(  # pragma: allowlist secret
        r'WAGTAILTRANSFER_SECRET_KEY\s*=\s*(?:"""(.*?)"""|\'\'\'(.*?)\'\'\')',
        re.DOTALL | re.IGNORECASE,
    )

    multiline_patterns = ((_TRIPLE_QUOTE, _extract_quoted),)

    def analyze_string(self, line: str, **kwargs: Any) -> Generator[str, None, None]:
        for match in self.WAGTAIL_TRANSFER_KEY_PATTERN.finditer(line):
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
