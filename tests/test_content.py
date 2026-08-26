import pytest

from app.content import make_excerpt, render_markdown, slug_from_title, unique_slug


def test_markdown_is_rendered_and_raw_html_is_escaped():
    rendered = render_markdown(
        "## Naslov\n\n**krepko** [povezava](https://example.com)\n\n<script>alert(1)</script>"
    )

    assert "<h2>Naslov</h2>" in rendered
    assert "<strong>krepko</strong>" in rendered
    assert 'href="https://example.com"' in rendered
    assert "&lt;script&gt;" in rendered
    assert "<script>" not in rendered


def test_markdown_removes_images_and_unsafe_links():
    rendered = render_markdown("![slika](https://example.com/a.jpg) [nevarno](javascript:alert(1))")

    assert "<img" not in rendered
    assert "javascript:" not in rendered


def test_excerpt_is_plain_text_and_shortened():
    excerpt = make_excerpt("To je **zelo dolg** zapis, ki ga bomo skrajšali.", max_length=20)

    assert "<" not in excerpt
    assert "**" not in excerpt
    assert excerpt.endswith("…")
    assert len(excerpt) <= 20


def test_slovenian_slug_transliterates_characters():
    assert slug_from_title("Čudovita Šola Življenja") == "cudovita-sola-zivljenja"


def test_unique_slug_handles_reserved_and_colliding_values():
    used = {"novice-2", "moja-novica"}

    assert unique_slug("Novice", used.__contains__) == "novice-3"
    assert unique_slug("Moja novica", used.__contains__) == "moja-novica-2"


def test_empty_slug_source_is_rejected():
    with pytest.raises(ValueError):
        slug_from_title("!!!")
