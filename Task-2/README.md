# User Authentication & Role-Based Access Control

A mini-project that demonstrates secure user authentication and role-based authorization using **FastAPI, JWT, SQLite, and Streamlit**.

The FastAPI backend handles registration, login, password hashing, token validation, and access control. The Streamlit application provides an interactive interface for users and administrators.

## Features

- User registration with username, email, and password.
- Password hashing using bcrypt.
- Login with username or email.
- Signed JWT access tokens with configurable expiration.
- Protected endpoints using bearer-token authentication.
- Role-based access for `user` and `admin accounts.
- User profile and protected-content views.
- Admin dashboard for viewing registered users.
- SQLite database managed through SQLAlchemy.
- Interactive Streamlit frontend connected to the FastAPI API.

## Tech Stack

| Component | Technologies |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Database | SQLite, SQLAlchemy 2.x |
| Validation | Pydantic 2.x |
| Authentication | JWT, python-jose, OAuth2 |
| Password security | Passlib, bcrypt |
| Frontend | Streamlit |
| API communication | Requests |

## Project Structure

```text
Task-2/
├── main.py                  # FastAPI application and API routes
├── database.py              # Database connection and sessions
├── models.py                # SQLAlchemy user model
├── schemas.py               # Pydantic request/response schemas
├── security.py              # Password hashing and JWT functions
├── dependencies.py          # Authentication and role dependencies
├── create_admin.py          # Script for creating an admin account
├── requirements.txt         # Project dependencies
├── .env.example             # Environment variable template
└── frontend/
    ├── app.py               # Streamlit user interface
    ├── api.py               # FastAPI request functions
    └── requirements.txt     # Frontend dependencies
```

The SQLite database (`auth.db`) is created automatically when the application initializes.

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Git (optional, for cloning the repository)

### 1. Open the project folder

Open PowerShell in the `Task-2` directory.

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, you can use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The main requirements file includes the backend and Streamlit dependencies. The separate frontend requirements file is also available if you want to install the UI dependencies independently:

```powershell
pip install -r frontend/requirements.txt
```

### 4. Configure environment variables

Create your local `.env` file:

```powershell
Copy-Item .env.example .env
```

Generate a secure secret key:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated value into `.env` as the value of `SECRET_KEY`. Keep your `.env` file private and do not commit it to GitHub.

### 5. Create an administrator account

Run the admin setup script:

```powershell
python create_admin.py <username> <email> <password>
```

Replace the placeholders with your chosen credentials. Public registration creates regular user accounts only; administrator accounts are created separately using this script.

### 6. Start the applications

Run the backend and frontend in two separate PowerShell terminals. Activate the virtual environment in both terminals.

**Terminal 1 — FastAPI backend**

```powershell
uvicorn main:app --reload
```

API base URL: http://127.0.0.1:8000

Swagger documentation: http://127.0.0.1:8000/docs

**Terminal 2 — Streamlit frontend**

From the `Task-2` directory, run:

```powershell
streamlit run frontend/app.py
```

Streamlit interface: http://localhost:8501

Keep the FastAPI server running while using the Streamlit application.

## API Endpoints

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/register` | Public | Register a regular user |
| `POST` | `/login` | Public | Authenticate and receive a JWT |
| `GET` | `/users/me` | Authenticated | Get the current user's profile |
| `GET` | `/protected` | Authenticated | Access protected content |
| `GET` | `/admin` | Admin | Access the admin-only route |
| `GET` | `/admin/users` | Admin | View registered users |

## Roles and Permissions

| Feature | User | Admin |
|---|:---:|:---:|
| Register an account | Yes | Created separately |
| Log in | Yes | Yes |
| View own profile | Yes | Yes |
| Access protected route | Yes | Yes |
| Access admin route | No | Yes |
| View all users | No | Yes |

Authorization is enforced by the FastAPI backend. Hiding admin features in the frontend is only a UI convenience and is not the security mechanism.

## Authentication Flow

1. A user registers through the API or Streamlit interface.
2. The backend hashes the password and stores the user record in SQLite.
3. The user logs in with their username or email and password.
4. FastAPI verifies the credentials and returns a signed JWT access token.
5. The frontend sends the token in the `Authorization: Bearer <token>` header when calling protected endpoints.
6. FastAPI validates the token and checks the user's role before granting access.

## Security Notes

- Passwords are stored as bcrypt hashes, never as plain text.
- JWT signing configuration is loaded from environment variables.
- Access tokens expire after the configured period (30 minutes by default).
- Public registration cannot assign the administrator role.
- Protected routes require a valid bearer token.
- Admin routes require the authenticated user's database role to be `admin`.
- The local `.env` file and SQLite database are excluded from version control by `.gitignore`.

## Testing

Use Swagger UI at http://127.0.0.1:8000/docs or the Streamlit interface to verify the application.

Suggested checks:

1. Register a new user and log in.
2. Open the user profile and protected route.
3. Try an admin endpoint with a regular user; access should be denied.
4. Log in with the administrator account and open the admin panel.
5. Verify that missing, invalid, or expired tokens cannot access protected endpoints.

## Notes

This project is intended for learning and demonstration. It uses a local SQLite database and a simple JWT-based authentication flow; it is not presented as a production-ready identity platform.
