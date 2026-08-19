"""Small, stdlib-only guards for network and XML developer tooling.

The helpers in this module are intentionally narrow.  They do not make an
arbitrary URL or XML document safe; they enforce the constraints used by
Regula's own maintenance commands:

* HTTPS only, with an explicit hostname allowlist that is re-checked after
  redirects; and
* bounded XML with declarations that can introduce entities or external
  subsets refused before parsing.

Keeping the checks here avoids six subtly different versions of the same
boundary while preserving the project's dependency-free core.
"""
from __future__ import annotations

import urllib.request
from pathlib import Path
from urllib.parse import urlsplit
# Parsing is bounded and declarations are refused before use.
from xml.etree import ElementTree  # nosec B405


DEFAULT_XML_LIMIT = 2_000_000


class UnsafeUrlError(ValueError):
    """A URL falls outside the caller's explicit HTTPS boundary."""


class UnsafeXmlError(ValueError):
    """XML exceeds the size boundary or contains a refused declaration."""


def validate_https_url(url: str, allowed_hosts: set[str] | frozenset[str]) -> str:
    """Return *url* after enforcing HTTPS, default port and an exact host.

    Hostname checks use :attr:`SplitResult.hostname`, not substring matching.
    User information is refused so a display such as ``trusted@attacker``
    cannot be mistaken for the destination.
    """
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    allowed = {item.lower().rstrip(".") for item in allowed_hosts}
    if parsed.scheme.lower() != "https":
        raise UnsafeUrlError("only HTTPS URLs are permitted")
    if parsed.username is not None or parsed.password is not None:
        raise UnsafeUrlError("URL user information is not permitted")
    try:
        port = parsed.port
    except ValueError as exc:
        raise UnsafeUrlError("URL port is invalid") from exc
    if port not in (None, 443):
        raise UnsafeUrlError("only the default HTTPS port is permitted")
    if host not in allowed:
        raise UnsafeUrlError(f"URL host is not permitted: {host or '<missing>'}")
    return url


class _AllowlistedRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, allowed_hosts: set[str] | frozenset[str]):
        self.allowed_hosts = frozenset(allowed_hosts)
        super().__init__()

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_https_url(newurl, self.allowed_hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def urlopen_https(
    request_or_url,
    *,
    allowed_hosts: set[str] | frozenset[str],
    timeout: int,
):
    """Open an allowlisted HTTPS request and police every redirect target."""
    url = (
        request_or_url.full_url
        if isinstance(request_or_url, urllib.request.Request)
        else str(request_or_url)
    )
    validate_https_url(url, allowed_hosts)
    opener = urllib.request.build_opener(_AllowlistedRedirectHandler(allowed_hosts))
    return opener.open(request_or_url, timeout=timeout)  # nosemgrep: dynamic-urllib-use-detected -- exact scheme/host and redirects validated above


def _checked_xml_bytes(source: str | bytes, *, max_bytes: int) -> bytes:
    raw = source if isinstance(source, bytes) else source.encode("utf-8")
    if len(raw) > max_bytes:
        raise UnsafeXmlError(
            f"XML input is {len(raw)} bytes; maximum permitted is {max_bytes}"
        )
    folded = raw.upper()
    if b"<!DOCTYPE" in folded or b"<!ENTITY" in folded:
        raise UnsafeXmlError("DTD and entity declarations are not permitted")
    return raw


def parse_xml_text(source: str | bytes, *, max_bytes: int = DEFAULT_XML_LIMIT):
    """Parse bounded XML after refusing DTD and entity declarations."""
    raw = _checked_xml_bytes(source, max_bytes=max_bytes)
    try:
        # Size is capped and declarations are refused immediately above.
        return ElementTree.fromstring(raw)  # nosec B314
    except ElementTree.ParseError as exc:
        raise UnsafeXmlError(f"XML could not be parsed: {exc}") from exc


def parse_xml_file(path: str | Path, *, max_bytes: int = DEFAULT_XML_LIMIT):
    """Read and parse a bounded XML file without following parser inclusions."""
    source = Path(path)
    size = source.stat().st_size
    if size > max_bytes:
        raise UnsafeXmlError(
            f"XML file is {size} bytes; maximum permitted is {max_bytes}: {source}"
        )
    return parse_xml_text(source.read_bytes(), max_bytes=max_bytes)
