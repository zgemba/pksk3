def test_public_pages_include_local_assets_and_security_headers(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"/static/vendor/bootstrap/bootstrap.min.css" in response.data
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert client.get("/static/vendor/bootstrap/bootstrap.min.css").status_code == 200
    assert client.get("/static/vendor/bootstrap/bootstrap.bundle.min.js").status_code == 200


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
    assert "Strani ni mogoče najti" in missing.get_data(as_text=True)
