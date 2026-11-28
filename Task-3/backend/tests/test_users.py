import pytest


async def test_create_user_success(client):
    response = await client.post(
        "/users/",
        json={"username": "alice", "email": "alice@example.com", "password": "StrongPass123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    assert "created_at" in body


async def test_password_is_never_returned(client, make_user):
    created = await make_user()
    fetched = (await client.get(f"/users/{created['id']}")).json()
    listed = (await client.get("/users/")).json()[0]
    for body in (created, fetched, listed):
        assert "password" not in body
        assert "password_hash" not in body


async def test_email_is_stored_in_lowercase(make_user):
    user = await make_user(email="Alice@Example.COM")
    assert user["email"] == "alice@example.com"


async def test_get_all_users(client, make_user):
    assert (await client.get("/users/")).json() == []
    await make_user()
    await make_user()
    response = await client.get("/users/")
    assert response.status_code == 200
    assert [u["id"] for u in response.json()] == [1, 2]


async def test_get_user_by_id(client, make_user):
    user = await make_user(username="bob")
    response = await client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    assert response.json()["username"] == "bob"
    assert response.json()["notes"] == []


async def test_duplicate_email_is_rejected(client, make_user):
    await make_user(email="same@example.com")
    response = await client.post(
        "/users/",
        json={"username": "other", "email": "same@example.com", "password": "StrongPass123"},
    )
    assert response.status_code == 409
    assert len((await client.get("/users/")).json()) == 1


async def test_duplicate_email_ignores_case(client, make_user):
    await make_user(email="same@example.com")
    response = await client.post(
        "/users/",
        json={"username": "other", "email": "SAME@example.com", "password": "StrongPass123"},
    )
    assert response.status_code == 409


async def test_get_nonexistent_user_returns_404(client):
    response = await client.get("/users/999")
    assert response.status_code == 404
    assert "999" in response.json()["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        {"username": "ab", "email": "a@example.com", "password": "StrongPass123"},  # username too short
        {"username": "alice", "email": "not-an-email", "password": "StrongPass123"},
        {"username": "alice", "email": "a@example.com", "password": "short"},
        {"username": "alice", "email": "a@example.com"},  # missing password
    ],
)
async def test_invalid_user_payload_returns_422(client, payload):
    response = await client.post("/users/", json=payload)
    assert response.status_code == 422


async def test_service_endpoints(client):
    assert (await client.get("/")).status_code == 200
    health = await client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "database": "connected"}
