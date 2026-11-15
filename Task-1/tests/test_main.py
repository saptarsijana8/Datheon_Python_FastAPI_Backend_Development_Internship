
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import data

client = TestClient(app)


# Reset sample data before each test
@pytest.fixture(autouse=True)
def reset_books():
    original_books = data.books.copy()
    original_next_id = data.next_id

    data.books.clear()
    data.books.update({
        1: {
            "id": 1,
            "title": "Python Crash Course",
            "author": "Eric Matthes",
            "price": 599.0,
            "quantity": 10
        },
        2: {
            "id": 2,
            "title": "Clean Code",
            "author": "Robert Martin",
            "price": 750.5,
            "quantity": 5
        },
        3: {
            "id": 3,
            "title": "Atomic Habits",
            "author": "James Clear",
            "price": 450.0,
            "quantity": 20
        }
    })
    data.next_id = 4

    yield

    data.books.clear()
    data.books.update(original_books)
    data.next_id = original_next_id


def test_home():
    response = client.get("/")
    assert response.status_code == 200


def test_get_all_books():
    response = client.get("/books")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_book_by_id():
    response = client.get("/books/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Python Crash Course"


def test_filter_books():
    response = client.get("/books?author=James")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_book():
    book = {
        "title": "Learning FastAPI",
        "author": "John Smith",
        "price": 500,
        "quantity": 10
    }

    response = client.post("/books", json=book)

    assert response.status_code == 201
    assert response.json()["id"] == 4


def test_invalid_book():
    book = {
        "title": "Invalid Book",
        "author": "John Smith",
        "price": -100,
        "quantity": 5
    }

    response = client.post("/books", json=book)
    assert response.status_code == 422


def test_book_not_found():
    response = client.get("/books/999")
    assert response.status_code == 404


def test_update_book():
    book = {
        "title": "Updated Python",
        "author": "John Smith",
        "price": 600,
        "quantity": 15
    }

    response = client.put("/books/1", json=book)

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Python"


def test_delete_book():
    response = client.delete("/books/1")

    assert response.status_code == 200
    assert client.get("/books/1").status_code == 404
