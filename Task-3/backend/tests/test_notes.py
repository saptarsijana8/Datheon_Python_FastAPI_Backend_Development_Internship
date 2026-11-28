import pytest


async def test_create_note_success(client, make_user):
    user = await make_user()
    response = await client.post(
        "/notes/", json={"title": "Shopping", "content": "Milk", "user_id": user["id"]}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Shopping"
    assert body["content"] == "Milk"
    assert body["user_id"] == user["id"]
    assert body["created_at"] and body["updated_at"]


async def test_create_note_for_nonexistent_user_is_rejected(client):
    response = await client.post("/notes/", json={"title": "Orphan", "user_id": 999})
    assert response.status_code == 404
    assert (await client.get("/notes/")).json() == []


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "", "user_id": 1},
        {"title": "   ", "user_id": 1},
        {"user_id": 1},
        {"title": "No user"},
        {"title": "Bad user", "user_id": 0},
    ],
)
async def test_invalid_note_payload_returns_422(client, make_user, payload):
    await make_user()
    assert (await client.post("/notes/", json=payload)).status_code == 422


async def test_get_all_notes(client, make_user, make_note):
    user = await make_user()
    assert (await client.get("/notes/")).json() == []
    await make_note(user["id"], title="One")
    await make_note(user["id"], title="Two")
    response = await client.get("/notes/")
    assert response.status_code == 200
    assert [n["title"] for n in response.json()] == ["One", "Two"]


async def test_get_note_by_id(client, make_user, make_note):
    user = await make_user()
    note = await make_note(user["id"], title="Find me")
    response = await client.get(f"/notes/{note['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Find me"


async def test_get_missing_note_returns_404(client):
    assert (await client.get("/notes/999")).status_code == 404


async def test_update_note(client, make_user, make_note):
    user = await make_user()
    note = await make_note(user["id"], title="Old", content="Keep me")
    response = await client.put(f"/notes/{note['id']}", json={"title": "New"})
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "New"
    assert body["content"] == "Keep me"  # untouched field stays the same
    assert body["updated_at"] >= note["updated_at"]
    assert body["created_at"] == note["created_at"]
    # the change is really stored, not just echoed
    assert (await client.get(f"/notes/{note['id']}")).json()["title"] == "New"


async def test_update_note_content_only(client, make_user, make_note):
    user = await make_user()
    note = await make_note(user["id"], title="Title", content="Old")
    body = (await client.put(f"/notes/{note['id']}", json={"content": ""})).json()
    assert body["title"] == "Title"
    assert body["content"] == ""


@pytest.mark.parametrize(
    "payload", [{}, {"title": None}, {"content": None}, {"title": ""}]
)
async def test_invalid_note_update_returns_422(client, make_user, make_note, payload):
    user = await make_user()
    note = await make_note(user["id"])
    assert (await client.put(f"/notes/{note['id']}", json=payload)).status_code == 422


async def test_update_missing_note_returns_404(client):
    response = await client.put("/notes/999", json={"title": "Nope"})
    assert response.status_code == 404


async def test_delete_note(client, make_user, make_note):
    user = await make_user()
    note = await make_note(user["id"])
    response = await client.delete(f"/notes/{note['id']}")
    assert response.status_code == 204
    assert (await client.get(f"/notes/{note['id']}")).status_code == 404
    assert (await client.get("/notes/")).json() == []


async def test_delete_missing_note_returns_404(client):
    assert (await client.delete("/notes/999")).status_code == 404


async def test_notes_belonging_to_a_user(client, make_user, make_note):
    alice = await make_user()
    bob = await make_user()
    await make_note(alice["id"], title="A1")
    await make_note(alice["id"], title="A2")
    await make_note(bob["id"], title="B1")

    response = await client.get(f"/users/{alice['id']}/notes")
    assert response.status_code == 200
    assert [n["title"] for n in response.json()] == ["A1", "A2"]
    assert {n["user_id"] for n in response.json()} == {alice["id"]}


async def test_user_without_notes_returns_empty_list(client, make_user):
    user = await make_user()
    response = await client.get(f"/users/{user['id']}/notes")
    assert response.status_code == 200
    assert response.json() == []


async def test_notes_of_nonexistent_user_returns_404(client):
    assert (await client.get("/users/999/notes")).status_code == 404


async def test_get_user_includes_notes_through_relationship(client, make_user, make_note):
    user = await make_user()
    await make_note(user["id"], title="Linked 1")
    await make_note(user["id"], title="Linked 2")
    body = (await client.get(f"/users/{user['id']}")).json()
    assert [n["title"] for n in body["notes"]] == ["Linked 1", "Linked 2"]
