"""Content processing helpers shared by posts and static pages."""

from __future__ import annotations

import html
import re
from collections.abc import Callable, Iterable

import bleach
import markdown
from slugify import slugify


ALLOWED_TAGS = frozenset(
    {
        "a",
        "blockquote",
        "br",
        "code",
        "em",
        "h2",
        "h3",
        "h4",
        "li",
        "ol",
        "p",
        "pre",
        "strong",
        "ul",
    }
)
ALLOWED_ATTRIBUTES = {"a": ["href", "title"]}
ALLOWED_PROTOCOLS = frozenset({"http", "https", "mailto"})
RESERVED_SLUGS = frozenset({"admin", "auth", "novice", "static", "login", "logout"})
_WHITESPACE = re.compile(r"\s+")


def render_markdown(source: str | None) -> str:
    """Render Markdown while rejecting raw HTML and unsafe links."""

    source = source or ""
    # Escape source HTML before Markdown sees it. This prevents allowed output
    # tags from being used as raw HTML input.
    escaped_source = html.escape(source, quote=False)
    rendered = markdown.markdown(escaped_source, extensions=["extra", "sane_lists"])
    return bleach.clean(
        rendered,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def plain_text(source: str | None) -> str:
    """Return normalized plain text from Markdown source."""

    rendered = render_markdown(source)
    text = bleach.clean(rendered, tags=[], strip=True)
    return _WHITESPACE.sub(" ", html.unescape(text)).strip()


def make_excerpt(source: str | None, max_length: int = 180) -> str:
    """Create a short excerpt, ending at a word boundary when possible."""

    if max_length < 1:
        raise ValueError("max_length must be positive")

    text = plain_text(source)
    if len(text) <= max_length:
        return text

    shortened = text[: max_length - 1].rsplit(" ", 1)[0].rstrip()
    return f"{shortened}…" if shortened else f"{text[: max_length - 1]}…"


def slug_from_title(title: str) -> str:
    """Create a URL-safe slug, transliterating Slovenian characters."""

    result = slugify(title, lowercase=True, separator="-", allow_unicode=False)
    if not result:
        raise ValueError("title must contain at least one alphanumeric character")
    return result


def unique_slug(
    title: str,
    exists: Callable[[str], bool],
    *,
    reserved: Iterable[str] = RESERVED_SLUGS,
) -> str:
    """Return an available slug, suffixing collisions with ``-2``, ``-3``, etc."""

    base = slug_from_title(title)
    reserved_set = {item.casefold() for item in reserved}
    candidate = base
    suffix = 2
    while candidate.casefold() in reserved_set or exists(candidate):
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate
