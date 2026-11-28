"""HTTP client for the FastAPI backend. Contains no Streamlit code on purpose."""

import os
from typing import Any

import requests

DEFAULT_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT_SECONDS = 10


class APIError(Exception):
    """The backend answered with an error, or its answer could not be understood."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class APIConnectionError(APIError):
    """The backend could not be reached at all."""


def _error_message(response: requests.Response) -> str:
    """Turn a FastAPI error body into one readable sentence."""
    try:
        detail = response.json()["detail"]
    except (ValueError, KeyError, TypeError):
        return f"Request failed with status {response.status_code}."
    if isinstance(detail, list):  # validation errors (422) are a list of problems
        problems = []
        for item in detail:
            field = ".".join(str(part) for part in item.get("loc", [])[1:])
            problems.append(f"{field}: {item.get('msg', 'invalid value')}" if field else item.get("msg", "invalid value"))
        return "; ".join(problems)
    return str(detail)


class APIClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL) -> None:
        self.base_url = base_url.strip().rstrip("/")

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        try:
            response = requests.request(method, url, timeout=TIMEOUT_SECONDS, **kwargs)
        except requests.exceptions.ConnectionError as exc:
            raise APIConnectionError(
                f"Cannot connect to the backend at {self.base_url}. "
                "Make sure the FastAPI server is running."
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise APIConnectionError(f"The backend at {self.base_url} took too long to respond.") from exc
        except requests.exceptions.RequestException as exc:  # e.g. a malformed URL
            raise APIError(f"Invalid request to {url}: {exc}") from exc

        if not response.ok:
            raise APIError(_error_message(response), response.status_code)
        if response.status_code == 204:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise APIError(f"{self.base_url} did not return JSON. Is this the Users & Notes API?") from exc

    # ----- service -----
    def health(self) -> dict[str, str]:
        return self._request("GET", "/health")

    # ----- users -----
    def list_users(self) -> list[dict]:
        return self._request("GET", "/users/")

    def get_user(self, user_id: int) -> dict:
        """A user plus their notes."""
        return self._request("GET", f"/users/{user_id}")

    def create_user(self, username: str, email: str, password: str) -> dict:
        return self._request(
            "POST", "/users/", json={"username": username, "email": email, "password": password}
        )

    # ----- notes -----
    def list_notes(self) -> list[dict]:
        return self._request("GET", "/notes/")

    def create_note(self, user_id: int, title: str, content: str) -> dict:
        return self._request(
            "POST", "/notes/", json={"user_id": user_id, "title": title, "content": content}
        )

    def update_note(self, note_id: int, title: str, content: str) -> dict:
        return self._request("PUT", f"/notes/{note_id}", json={"title": title, "content": content})

    def delete_note(self, note_id: int) -> None:
        self._request("DELETE", f"/notes/{note_id}")
