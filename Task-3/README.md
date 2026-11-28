# Database Persistence: Users & Notes API

A beginner-friendly project that shows how to **store application data permanently** with
**FastAPI**, **async SQLAlchemy 2.0** and **SQLite**, plus an interactive **Streamlit** dashboard that talks to the API.

**Quick start (after cloning):**

```bash
python -m venv .venv                 # create a virtual environment
# activate it (see section 11), then:
pip install -r requirements.txt      # one file installs everything
python run.py                        # starts the backend AND the frontend together
```

Then open **http://localhost:8501** (dashboard) and **http://127.0.0.1:8000/docs** (API docs).

---

## 1. Project overview

This project is a *User and Notes Management* application. Users can be created, and each user
can own many notes. Everything is saved in a SQLite file (`backend/notes.db`), so the data is
still there after the server is stopped and started again. A Streamlit web app gives you a
friendly, interactive interface on top of the REST API.

## 2. Project objective

Replace temporary in-memory storage (Python lists/dicts, which disappear on restart) with a real
relational database, and demonstrate:

- permanent storage in SQLite,
- a one-to-many relationship (one user → many notes) with primary and foreign keys,
- asynchronous database sessions (`AsyncSession`),
- full CRUD operations through a REST API,
- an automated test suite, and a UI that uses the API (not the database directly).

## 3. Problem statement

A simple API that keeps data in a Python list loses everything when the server restarts, cannot
enforce relationships between records, and cannot be shared between processes. A relational
database solves this: data is stored on disk, the database enforces rules (unique emails, valid
foreign keys), and related records can be queried together.

## 4. Key features

**Backend**

- Create and read users; passwords are hashed with **Argon2** and never returned by the API.
- Create, read, update and delete notes; every note belongs to exactly one existing user.
- Duplicate emails are rejected (HTTP 409); notes for unknown users are rejected (HTTP 404).
- SQLite **foreign keys are switched on**, so the database itself rejects orphan notes.
- Deleting a user also deletes their notes (`ON DELETE CASCADE`).
- `GET /users/{id}` returns a user together with their notes, loaded through the ORM relationship.
- Interactive API docs (Swagger UI), a root endpoint and a `/health` endpoint.
- 41 automated tests that use a separate temporary database.

**Frontend (Streamlit)**

- Modern look with a gradient header, avatar cards and hover effects; works in light and dark mode.
- Dashboard with live statistics, a "notes per user" bar chart and a 14-day activity chart.
- Pop-up dialogs for creating users, writing notes, editing notes and confirming deletes.
- Live form feedback: a requirements checklist and a password-strength meter while you type.
- Search, filter by user, sort, and a switch between **Cards** and **Table** views for notes.
- Toast notifications after every action, friendly empty states, and a clear "backend not reachable" screen with a Retry button.
- All user text is HTML-escaped, so notes cannot inject markup into the page.

## 5. Technology stack

| Part | Technology |
|---|---|
| Language | Python 3.11+ |
| API framework | FastAPI, served by Uvicorn |
| ORM | SQLAlchemy 2.0 (async: `AsyncSession`, `async_sessionmaker`) |
| Database | SQLite via `aiosqlite` |
| Validation | Pydantic v2 (plus `email-validator`) |
| Password hashing | `argon2-cffi` |
| Frontend | Streamlit, pandas (charts), `requests` |
| Testing | pytest, pytest-asyncio, HTTPX |

## 6. Project architecture

```
┌──────────────┐   HTTP (JSON)   ┌──────────────────────────────┐   SQL   ┌────────────┐
│  Streamlit   │ ──────────────► │  FastAPI                     │ ──────► │  SQLite    │
│  frontend    │ ◄────────────── │  routers → crud → SQLAlchemy │ ◄────── │  notes.db  │
└──────────────┘                 └──────────────────────────────┘         └────────────┘
   port 8501                              port 8000
```

- **Routers** (`routers/`) handle HTTP: parse requests, choose status codes, raise `HTTPException`.
- **CRUD** (`crud.py`) contains all database logic. Routers never write queries.
- **Models** (`models.py`) describe the tables; **schemas** (`schemas.py`) describe the JSON that goes in and out.
- **Database** (`database.py`) creates the engine and gives every request its own session (`get_db`).
- The **frontend never touches SQLite**. It only calls the REST API through `frontend/api_client.py`.
- The frontend finds the backend through the `API_BASE_URL` setting (default `http://127.0.0.1:8000`).
  `run.py` sets it for you.

## 7. Folder structure

Everything is run from the **project root** (the folder that contains `requirements.txt`).

```
database-persistence/
├── .github/workflows/task-3-tests.yml # GitHub Actions workflow (repository root)
├── .streamlit/config.toml        # Streamlit theme and settings
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app, startup, root and health endpoints
│   │   ├── database.py           # async engine, session factory, get_db, init_db
│   │   ├── models.py             # User and Note ORM models
│   │   ├── schemas.py            # Pydantic request/response schemas
│   │   ├── crud.py               # async database operations
│   │   ├── security.py           # Argon2 password hashing
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       └── notes.py
│   └── tests/
│       ├── conftest.py           # temporary test database + HTTP client fixtures
│       ├── test_users.py
│       ├── test_notes.py
│       └── test_persistence.py
├── frontend/
│   ├── api_client.py             # all HTTP calls to the backend
│   └── app.py                    # Streamlit UI
├── .gitattributes                # consistent line endings on Windows/macOS/Linux
├── .gitignore
├── pytest.ini
├── README.md
├── requirements.txt              # ONE file: backend + frontend + testing
└── run.py                        # starts backend and frontend together
```

`backend/notes.db` is created automatically the first time the backend starts. It is git-ignored.

## 8. Database schema

**users**

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | primary key |
| `username` | VARCHAR(50) | required |
| `email` | VARCHAR(255) | required, **unique** (stored in lowercase) |
| `password_hash` | VARCHAR(255) | required (Argon2 hash, never the password) |
| `created_at` | DATETIME | required (UTC) |

**notes**

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | primary key |
| `title` | VARCHAR(200) | required |
| `content` | TEXT | required (may be an empty string) |
| `user_id` | INTEGER | required, **foreign key → users.id**, `ON DELETE CASCADE` |
| `created_at` | DATETIME | required (UTC) |
| `updated_at` | DATETIME | required (UTC), refreshed on every update |

## 9. The Users → Notes relationship

```
users (1) ───────────< notes (many)
  id  ◄──────────────── user_id
```

- **One user has many notes**, and **each note belongs to exactly one user**.
- In SQL this is the `notes.user_id` foreign key pointing at `users.id`.
- In SQLAlchemy it is two linked attributes: `User.notes` (a list) and `Note.user` (a single user).
- `GET /users/{id}` uses an explicit SQL `LEFT OUTER JOIN` with `contains_eager(User.notes)`.
  This returns the user and their notes in one joined query while still including users who have no notes.
- The query calls `unique()` because a JOIN returns one result row per related note; SQLAlchemy then
  assembles those rows into one user object with its notes collection.
- SQLite does **not** enforce foreign keys by default. `database.py` runs `PRAGMA foreign_keys=ON`
  on every new connection, so the database rejects a note whose `user_id` does not exist.
- Deleting a user deletes their notes (cascade). The API has no "delete user" endpoint, but the
  cascade is covered by a test.

## 10. Prerequisites

- **Python 3.11 or newer** (`python --version`)
- **pip** (comes with Python)
- A terminal (PowerShell on Windows)
- Git (to clone and to push to GitHub)

## 11. Installation

### 11.1 Get the code

```powershell
git clone <your-repository-url> database-persistence
cd database-persistence
```

### 11.2 Create and activate a virtual environment (project root)

A virtual environment keeps this project's packages separate from the rest of your computer.
One environment at the project root is used by both the backend and the frontend.

**Windows PowerShell** (working directory: `database-persistence`)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the script, run this once in the same window and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your prompt should now start with `(.venv)`. Activate the environment again in every new terminal.

### 11.3 Install all dependencies (backend + frontend + tests)

Working directory: `database-persistence`

```powershell
pip install -r requirements.txt
```

This one file installs everything: FastAPI, SQLAlchemy and friends for the backend, Streamlit
for the frontend, and pytest for the tests.

## 12. Database initialization

There is nothing to run manually. When the backend starts, `init_db()` (in `database.py`) calls
`Base.metadata.create_all()`, which creates the `users` and `notes` tables **only if they do not
exist yet**. An existing database file and its data are never overwritten or recreated.

**Limitations of `create_all()`:** it never changes tables that already exist. If you later add a
column or rename a field, `create_all()` will not update the existing table. For real projects you
would add a migration tool such as [Alembic](https://alembic.sqlalchemy.org/) (it has an async
template: `alembic init -t async migrations`), which records each schema change as a versioned
migration script. For this learning project, `create_all()` is the simplest reliable option.
If you change the models during development and don't need the old data, stop the servers and
delete `backend/notes.db`.

By default the database is `backend/notes.db`. To use another location, set the `DATABASE_URL`
environment variable before starting the backend, for example
`$env:DATABASE_URL = "sqlite+aiosqlite:///C:/data/my_notes.db"`.

## 13. Running the application (backend and frontend together)

The frontend needs the backend, so both must be running. Pick **one** of the two options.
In both, the working directory is the project root, `database-persistence`, with the virtual
environment active.

### Option A: one command (recommended)

```powershell
python run.py
```

On Linux/macOS use `python3 run.py`. This starts the backend, waits until it is healthy, then
starts the frontend and points it at the backend. Your browser opens the dashboard automatically.
Press **Ctrl+C once** to stop both.

| Option | Meaning |
|---|---|
| `--backend-port 9000` | run the API on another port (the frontend is configured automatically) |
| `--frontend-port 9501` | run the dashboard on another port |
| `--reload` | restart the backend automatically when you edit backend code |
| `--no-browser` | do not open a browser window |

### Option B: two terminals (see each server's logs separately)

**Terminal 1: backend**

```powershell
uvicorn app.main:app --app-dir backend --reload --reload-dir backend
```

Wait for `Uvicorn running on http://127.0.0.1:8000`.

**Terminal 2: frontend** (open a new terminal, activate the virtual environment again, `cd` into the project root)

```powershell
streamlit run frontend/app.py
```

If Streamlit asks for an email address on first start, just press Enter.
Start the backend **first**; if the frontend opens before the backend is ready, click **Retry**.

### Addresses

| URL | Purpose |
|---|---|
| http://localhost:8501 | Streamlit dashboard |
| http://127.0.0.1:8000/docs | Swagger UI (try every endpoint in the browser) |
| http://127.0.0.1:8000/redoc | ReDoc documentation |
| http://127.0.0.1:8000/health | Health check (also tests the database connection) |
| http://127.0.0.1:8000/ | API information |

### Pointing the frontend at a different backend

The frontend reads `API_BASE_URL` (default `http://127.0.0.1:8000`). With `run.py` this is automatic.
When starting Streamlit by hand you can set it first, or change **Backend settings → API base URL**
in the dashboard sidebar:

```powershell
$env:API_BASE_URL = "http://127.0.0.1:9000"
streamlit run frontend/app.py
```

## 14. API endpoint reference

| Method | Endpoint | Description | Success | Errors |
|---|---|---|---|---|
| GET | `/` | API information | 200 | |
| GET | `/health` | Health check with database test | 200 | 503 |
| POST | `/users/` | Create a user | 201 | 409 duplicate email, 422 invalid data |
| GET | `/users/` | List all users | 200 | |
| GET | `/users/{user_id}` | Get a user **with their notes** | 200 | 404 |
| GET | `/users/{user_id}/notes` | List the notes of a user | 200 | 404 unknown user |
| POST | `/notes/` | Create a note for a user | 201 | 404 unknown user, 422 |
| GET | `/notes/` | List all notes | 200 | |
| GET | `/notes/{note_id}` | Get one note | 200 | 404 |
| PUT | `/notes/{note_id}` | Update title and/or content (send only what changes) | 200 | 404, 422 |
| DELETE | `/notes/{note_id}` | Delete a note | 204 | 404 |

Validation rules: username 3–50 characters; valid email; password 8–128 characters; note title
1–200 characters; note content up to 10,000 characters.

## 15. Example API requests and responses

The examples work as written against a fresh database. Timestamps are in UTC and will differ.

### Windows PowerShell

```powershell
# Create a user
$user = @{ username = "alice"; email = "alice@example.com"; password = "StrongPass123" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/users/ -ContentType "application/json" -Body $user

# Create a note for user 1
$note = @{ title = "Shopping list"; content = "Milk, eggs, bread"; user_id = 1 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/notes/ -ContentType "application/json" -Body $note

# Get the user together with their notes
Invoke-RestMethod -Uri http://127.0.0.1:8000/users/1 | ConvertTo-Json -Depth 5

# Update the note title
Invoke-RestMethod -Method Put -Uri http://127.0.0.1:8000/notes/1 -ContentType "application/json" -Body (@{ title = "Groceries" } | ConvertTo-Json)

# Delete the note
Invoke-RestMethod -Method Delete -Uri http://127.0.0.1:8000/notes/1
```

### Linux / macOS (curl)

```bash
curl -X POST http://127.0.0.1:8000/users/ -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"StrongPass123"}'

curl -X POST http://127.0.0.1:8000/notes/ -H "Content-Type: application/json" \
  -d '{"title":"Shopping list","content":"Milk, eggs, bread","user_id":1}'

curl http://127.0.0.1:8000/users/1
```

### Responses

`POST /users/` → `201 Created` (note: no password or hash)

```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "created_at": "2026-11-23T13:02:38.001246"
}
```

`POST /notes/` → `201 Created`

```json
{
  "id": 1,
  "title": "Shopping list",
  "content": "Milk, eggs, bread",
  "user_id": 1,
  "created_at": "2026-11-23T13:02:38.020041",
  "updated_at": "2026-11-23T13:02:38.020052"
}
```

`GET /users/1` → `200 OK` (user with notes loaded via the relationship)

```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "created_at": "2026-11-23T13:02:38.001246",
  "notes": [
    {
      "id": 1,
      "title": "Shopping list",
      "content": "Milk, eggs, bread",
      "user_id": 1,
      "created_at": "2026-11-23T13:02:38.020041",
      "updated_at": "2026-11-23T13:02:38.020052"
    }
  ]
}
```

Error examples: `POST /notes/` for a missing user → `404` `{"detail": "User 99 not found."}`;
a second user with the same email → `409` `{"detail": "A user with this email already exists."}`.

## 16. Using the Streamlit dashboard

Use the sidebar to switch pages. The sidebar also shows the connection status, the backend
settings, and a button that opens the API docs.

- **Dashboard**
  - A header, three statistic cards (users, notes, notes per user) and the four most recent notes.
  - A bar chart of notes per user and an area chart of notes created in the last 14 days.
  - Quick buttons: **＋ New user**, **＋ New note**, and **View all notes →**.
- **Users**
  - One card per user with an avatar, email, note count and join date.
  - Search by name or email; sort by newest, name or number of notes.
  - **View notes** opens a pop-up with the user's profile and all of their notes.
  - **＋ Note** opens the new-note pop-up with that user already selected.
  - **＋ New user** opens a pop-up with a live checklist and a password-strength meter.
    The **Create user** button reports anything that is still missing.
- **Notes**
  - Search title and content, filter by user, and sort (newest, oldest, recently edited, title A–Z).
  - **Cards** view: every card has **✏️ Edit** and **🗑️ Delete** buttons. Deleting asks
    "Are you sure?" in a pop-up first.
  - **Table** view: click a row, then choose Edit or Delete.
  - Long lists show 12 cards at a time with a **Show more** button.

Every change shows a toast notification. If the backend is not running, the app shows a
"Backend not reachable" screen with the start command and a **Retry** button instead of crashing.
Everything shown comes from the API, which reads it from SQLite.

## 17. Running the automated tests

Working directory: project root (virtual environment active). The servers do **not** need to be running.

```powershell
pytest
```

Useful variations: `pytest -v` (one line per test), `pytest backend/tests/test_notes.py` (one file).

The tests cover user and note CRUD, duplicate emails, unknown users/notes, validation errors, and
persistence. Every test uses its own temporary SQLite file, which is deleted afterwards. Your
development database `backend/notes.db` is never opened or changed by the tests.

## 18. Verifying persistent storage

1. Start the application (section 13) and open http://127.0.0.1:8000/docs or the dashboard.
2. Create a user, then add a note to that user.
3. Stop everything with `Ctrl+C`. Confirm http://127.0.0.1:8000/health no longer responds.
4. Start it again (`python run.py`).
5. Open the dashboard or call `GET /users/` and `GET /notes/`. **Your data is still there.**

To look inside the database file directly (working directory: project root):

```powershell
python -c "import sqlite3; c = sqlite3.connect('backend/notes.db'); print(c.execute('SELECT id, username, email FROM users').fetchall()); print(c.execute('SELECT id, title, user_id FROM notes').fetchall())"
```

(This one-liner is only for inspection. The application itself never uses synchronous database access.)

## 19. Pushing the project to GitHub

The repository is already prepared: `.gitignore` keeps your virtual environment, caches, `.env`
files and the local `notes.db` out of Git, `.gitattributes` keeps line endings consistent, and
`.github/workflows/task-3-tests.yml` runs the Task-3 test suite when Task-3 files change (Python 3.11 and 3.12).

1. Create an **empty** repository on GitHub (no README, no .gitignore, no license).
2. In the project root:

```powershell
git init
git add .
git status          # check: no .venv, no notes.db, no __pycache__ in the list
git commit -m "Initial commit: Users & Notes API with Streamlit dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repository>.git
git push -u origin main
```

3. Open the **Actions** tab of the repository to see the tests run.
4. Optional: show the test status in this README by adding
   `![Tests](https://github.com/<your-username>/<your-repository>/actions/workflows/tests.yml/badge.svg)`
   under the title.
5. Optional: if you want others to reuse the code, add a `LICENSE` file (GitHub's "Add file → Create new file → LICENSE" offers templates such as MIT).

Anyone who clones the repository then follows section 11 and section 13 to run it.

## 20. Common errors and troubleshooting

| Problem | Cause and fix |
|---|---|
| `uvicorn` / `streamlit` / `pytest` is "not recognized" | The virtual environment is not active in this terminal. Activate it (section 11.2) and retry. |
| PowerShell: "running scripts is disabled" | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again. |
| `ModuleNotFoundError` for fastapi, streamlit, … | Dependencies are not installed in the active environment. Run `pip install -r requirements.txt` from the project root. |
| `ModuleNotFoundError: No module named 'app'` | Run commands from the **project root** and keep `--app-dir backend` in the uvicorn command (or use `python run.py`). |
| Dashboard shows "Backend not reachable" | Start the backend first (or use `python run.py`), then click **Retry**. Check the URL under *Backend settings*. |
| `run.py`: "The backend stopped during startup" | Port 8000 is probably busy. Stop the other program, or use `python run.py --backend-port 8001`. |
| `Address already in use` / port busy | Another process uses the port. Stop it, or choose another port with `--backend-port` / `--frontend-port`. |
| Dashboard looks unthemed (no purple accent) | Streamlit reads `.streamlit/config.toml` from the folder you launch it in. Start it from the project root. |
| `307 Temporary Redirect` when calling `/users` | Use the trailing slash: `/users/` and `/notes/`. |
| `409 A user with this email already exists` | Emails are unique and compared in lowercase. Use another email. |
| `404 User N not found` when creating a note | The `user_id` does not exist. Create the user first. |
| `422 Unprocessable Entity` | The request data broke a validation rule (see section 14). The response says which field. |
| Database changed after editing models | `create_all()` does not alter existing tables (section 12). Delete `backend/notes.db` for a fresh start, or use migrations. |
| `database is locked` | Close other programs that have `notes.db` open (e.g. a DB browser with a write transaction). |
| `curl` in PowerShell behaves strangely | In PowerShell `curl` is an alias of `Invoke-WebRequest`. Use `Invoke-RestMethod` or `curl.exe`. |

Note: SQLite may reuse the id of the most recently deleted row, so a new record can get an id that an old, deleted record once had.

## 21. Future improvements

- Authentication (login with JWT) and per-user access control, using the stored password hashes.
- Alembic migrations instead of `create_all()`.
- Pagination and server-side search for notes and users.
- A "delete user" endpoint and endpoints to update users.
- Timezone-aware timestamps (for example PostgreSQL in production).
- Docker setup for one-command deployment.
- Automated UI tests for the Streamlit app.
