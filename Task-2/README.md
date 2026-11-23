# Authentication + RBAC Mini Project (FastAPI + JWT + Streamlit)

A FastAPI project with user registration, login, JWT access tokens,
role-based access control (`user` / `admin`), and a **Streamlit** frontend.

## Tech
- **Backend:** FastAPI + Uvicorn, SQLite + SQLAlchemy 2.x, Pydantic 2.x, python-jose (JWT), passlib[bcrypt]
- **Frontend:** Streamlit, Requests

## Windows setup

Open **PowerShell** in the `Task-2` folder.

```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# If you get an execution policy error, run once:
# Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
Copy-Item .env.example .env
# Open .env and set SECRET_KEY to a long random string. You can generate one with:
python -c "import secrets; print(secrets.token_hex(32))"

# 4. Create the admin account
python create_admin.py admin admin@example.com AdminPass123

# 5. Run the app
uvicorn main:app --reload
```

Open Swagger UI: `http://127.0.0.1:8000/docs`

### Quick test flow in /docs
1. `POST /register` — create a normal user.
2. Click **Authorize** (top right), enter:
   - **username**: your username (or email)
   - **password**: your password
   *(Swagger uses the OAuth2 password flow and calls `POST /login`)*
3. `GET /users/me` — returns your profile.
4. `GET /protected` — works for any logged-in user.
5. `GET /admin` — returns 403 for normal users.
6. Authorize again with the admin credentials, then:
   - `GET /admin` — returns a welcome message.
   - `GET /admin/users` — lists all users (no password hashes exposed).

## Endpoints

| Method | Path | Access |
|---|---|---|
| `POST` | `/register` | Public |
| `POST` | `/login` | Public (OAuth2 password form) |
| `GET` | `/users/me` | Authenticated |
| `GET` | `/protected` | Authenticated |
| `GET` | `/admin` | Admin |
| `GET` | `/admin/users` | Admin |

## Notes
- Public registration always creates role `user`.
- To create additional admins, run `python create_admin.py <username> <email> <password>`.
- Tokens expire after 30 minutes (configurable in `.env`).
- Passwords are hashed with bcrypt; plain-text passwords are never stored.

## Streamlit Frontend

### Install frontend dependencies

```powershell
pip install -r frontend/requirements.txt
```

### Run both applications

Open **two** PowerShell terminals in the `Task-2` folder (both with venv activated):

**Terminal 1 — FastAPI backend:**
```powershell
uvicorn main:app --reload
```

**Terminal 2 — Streamlit frontend:**
```powershell
streamlit run frontend/app.py
```

The frontend opens at `http://localhost:8501` and talks to the backend at `http://127.0.0.1:8000`.

### Frontend features
- **Login page** — authenticate with username/email and password.
- **Registration page** — create a new user account (always role `user`).
- **User dashboard** — view profile, fetch protected content, refresh profile.
- **Admin panel** — view all registered users, verify admin access (admin role only).
- Automatic logout on expired/invalid tokens.

### Project structure
```
Task-2/
├── main.py              # FastAPI app & endpoints
├── database.py          # SQLAlchemy engine & session
├── models.py            # User ORM model
├── schemas.py           # Pydantic request/response schemas
├── security.py          # JWT & password hashing
├── dependencies.py      # Auth & RBAC dependencies
├── create_admin.py      # CLI script to create admin users
├── requirements.txt     # Backend dependencies
├── .env.example         # Environment template
├── .env                 # Active environment config
└── frontend/
    ├── app.py           # Streamlit UI
    ├── api.py           # API client functions
    └── requirements.txt # Frontend dependencies
```
