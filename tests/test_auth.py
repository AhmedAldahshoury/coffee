def test_register_and_login(client):
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "pass123", "name": "Test User"},
    )
    assert register.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "pass123"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()
