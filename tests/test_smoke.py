def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "PKSK" in response.get_data(as_text=True)


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}
