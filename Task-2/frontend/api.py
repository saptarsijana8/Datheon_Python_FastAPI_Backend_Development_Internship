"""
api.py — Reusable functions to communicate with the FastAPI backend.

Every function returns a tuple: (success: bool, data: dict | str)
  - On success: (True, response_json_dict)
  - On failure: (False, error_message_string)
"""

import requests

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 10  # seconds


# ---------- helpers ----------

def _auth_header(token: str) -> dict:
    """Build the Authorization header for authenticated requests."""
    return {"Authorization": f"Bearer {token}"}


def _extract_error(response: requests.Response) -> str:
    """Pull the 'detail' field from a FastAPI error response, or fall back
    to the raw status text."""
    try:
        detail = response.json().get("detail", response.text)
    except Exception:
        detail = response.text
    return str(detail)


# ---------- public endpoints ----------

def register_user(username: str, email: str, password: str):
    """POST /register — sends JSON body."""
    try:
        resp = requests.post(
            f"{BASE_URL}/register",
            json={"username": username, "email": email, "password": password},
            timeout=TIMEOUT,
        )
        if resp.status_code == 201:
            return True, resp.json()
        return False, _extract_error(resp)
    except requests.ConnectionError:
        return False, "Cannot connect to the backend. Is FastAPI running?"
    except requests.Timeout:
        return False, "Request timed out. Try again."
    except Exception as e:
        return False, f"Unexpected error: {e}"


def login_user(username: str, password: str):
    """POST /login — sends form-encoded data (OAuth2PasswordRequestForm)."""
    try:
        resp = requests.post(
            f"{BASE_URL}/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return True, resp.json()          # {"access_token": ..., "token_type": "bearer"}
        return False, _extract_error(resp)
    except requests.ConnectionError:
        return False, "Cannot connect to the backend. Is FastAPI running?"
    except requests.Timeout:
        return False, "Request timed out. Try again."
    except Exception as e:
        return False, f"Unexpected error: {e}"


# ---------- authenticated endpoints ----------

def get_current_user(token: str):
    """GET /users/me"""
    try:
        resp = requests.get(
            f"{BASE_URL}/users/me",
            headers=_auth_header(token),
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return True, resp.json()
        return False, _extract_error(resp)
    except requests.ConnectionError:
        return False, "Cannot connect to the backend."
    except Exception as e:
        return False, f"Unexpected error: {e}"


def get_protected(token: str):
    """GET /protected"""
    try:
        resp = requests.get(
            f"{BASE_URL}/protected",
            headers=_auth_header(token),
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return True, resp.json()
        return False, _extract_error(resp)
    except requests.ConnectionError:
        return False, "Cannot connect to the backend."
    except Exception as e:
        return False, f"Unexpected error: {e}"


def get_admin(token: str):
    """GET /admin"""
    try:
        resp = requests.get(
            f"{BASE_URL}/admin",
            headers=_auth_header(token),
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return True, resp.json()
        if resp.status_code == 403:
            return False, "Admin privileges required."
        return False, _extract_error(resp)
    except requests.ConnectionError:
        return False, "Cannot connect to the backend."
    except Exception as e:
        return False, f"Unexpected error: {e}"


def get_all_users(token: str):
    """GET /admin/users"""
    try:
        resp = requests.get(
            f"{BASE_URL}/admin/users",
            headers=_auth_header(token),
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return True, resp.json()          # list of UserPublic dicts
        if resp.status_code == 403:
            return False, "Admin privileges required."
        return False, _extract_error(resp)
    except requests.ConnectionError:
        return False, "Cannot connect to the backend."
    except Exception as e:
        return False, f"Unexpected error: {e}"
