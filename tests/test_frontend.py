import re

from app import discover_banner_filenames, linkify_mailto


def test_banner_discovery_accepts_only_numbered_jpegs(tmp_path):
    banner_directory = tmp_path / "banners"
    banner_directory.mkdir()
    for filename in ("1.jpg", "2.jpg", "10.jpg", "01.jpg", "100.jpg", "banner.jpg", "3.png"):
        (banner_directory / filename).touch()

    assert discover_banner_filenames(tmp_path) == ("01.jpg", "1.jpg", "2.jpg", "10.jpg")


def test_linkify_mailto_escapes_other_html():
    rendered = linkify_mailto("Kontakt: mailto:info@example.com\n<strong>ne HTML</strong>")

    assert rendered == (
        'Kontakt: <a href="mailto:info@example.com">info@example.com</a>\n'
        "&lt;strong&gt;ne HTML&lt;/strong&gt;"
    )


def test_public_pages_include_local_assets_and_security_headers(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"/static/vendor/bootstrap/bootstrap.min.css" in response.data
    assert re.search(rb'/static/banners/(?:[1-9]|1[0-4])\.jpg', response.data)
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert client.get("/static/vendor/bootstrap/bootstrap.min.css").status_code == 200


def test_banner_is_not_rendered_on_auth_or_admin_pages(client):
    login = client.get("/auth/login")
    admin = client.get("/admin/", follow_redirects=False)

    assert b"/static/banners/" not in login.data
    assert admin.status_code == 302
    assert client.get("/static/vendor/bootstrap/bootstrap.bundle.min.js").status_code == 200


def test_footer_preserves_line_breaks(client, app):
    from app.extensions import db
    from app.models import SiteSettings

    with app.app_context():
        db.session.add(
            SiteSettings(
                site_name="PKSK",
                footer_text="Kontakt: mailto:info@example.com\nDruga vrstica",
            )
        )
        db.session.commit()

    response = client.get("/")

    assert b'class="container text-center footer-text"' in response.data
    assert b'<a href="mailto:info@example.com">info@example.com</a>' in response.data
    assert b"\nDruga vrstica" in response.data


def test_sitemap_robots_and_error_page(client):
    sitemap = client.get("/sitemap.xml")
    robots = client.get("/robots.txt")
    missing = client.get("/does-not-exist")

    assert sitemap.status_code == 200
    assert sitemap.mimetype == "application/xml"
    assert b"http://localhost/" in sitemap.data
    assert robots.status_code == 200
    assert b"Disallow: /admin/" in robots.data
    assert b"Sitemap: http://localhost/sitemap.xml" in robots.data
    assert missing.status_code == 404
    assert "Hmmm, strežnik se je izgubil" in missing.get_data(as_text=True)
