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


def test_register_and_login_with_long_password(client):
    long_password = "p" * 200
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "longpass@example.com", "password": long_password, "name": "Long Password"},
    )
    assert register.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "longpass@example.com", "password": long_password},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_register_duplicate_email_returns_409(client):
    payload = {"email": "dupe@example.com", "password": "pass123", "name": "Dupe"}
    first = client.post("/api/v1/auth/register", json=payload)
    second = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["code"] == "email_already_registered"
