def test_register_and_login(client):
    response = client.post("/api/v1/auth/register", json={"email": "hello@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

    login = client.post("/api/v1/auth/login", json={"email": "hello@example.com", "password": "password123"})
    assert login.status_code == 200
    assert "access_token" in login.json()
