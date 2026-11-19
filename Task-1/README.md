# 📚 BookStore Management System (REST API + Dashboard)

A bookstore project with two parts:

1. **Backend**: a REST API built with **Python, FastAPI and Pydantic**
2. **Frontend**: a **Streamlit dashboard** that uses the API, so books can be managed from a simple web interface

Books are stored in a Python dictionary (in memory), so no database is needed.

---

## ✨ Features

### Backend (FastAPI)
- View all books, or one book by its ID
- Add, update and delete books
- Search by title, filter by author, filter by minimum and maximum price
- Pydantic validation (no empty titles, no negative prices, no invalid quantities)
- Proper HTTP status codes and error messages
- Automatic Swagger UI documentation at `/docs`

### Frontend (Streamlit)
- 📊 **Dashboard**: total books, copies in stock, inventory value, average price, stock chart and low-stock list
- 📖 **All Books**: table of all books with search and filters
- ➕ **Add Book**: form to add a new book
- ✏️ **Update Book**: pick a book by ID, edit its details and save
- 🗑️ **Delete Book**: pick a book by ID and delete it after confirming
- Clear error messages, and a "Backend connected / offline" indicator in the sidebar

---

## 🛠️ Technologies Used

| Technology | Why it is used |
|---|---|
| **Python 3** | Programming language |
| **FastAPI** | Builds the REST API |
| **Pydantic** | Validates the data sent to the API |
| **Uvicorn** | Runs the FastAPI server |
| **Streamlit** | Builds the dashboard using only Python |
| **Requests** | Lets the dashboard talk to the API |

---

## 📁 Project Structure

```
Task-1/
├── app/
│   ├── __init__.py       # Makes "app" a Python package
│   ├── main.py           # API endpoints
│   ├── schemas.py        # Pydantic models (validation rules)
│   └── data.py           # Book storage (a Python dictionary)
├── .streamlit/
│   └── config.toml       # Blue and white theme for the dashboard
├── frontend.py           # Streamlit dashboard
├── requirements.txt      # Libraries to install
└── README.md             # This file
```

**How the parts connect**

```
Streamlit dashboard (frontend.py)  ──HTTP requests──►  FastAPI backend (app/main.py)
        port 8501                                            port 8000
```

The dashboard never stores data itself. Every action is sent to the API.

---

## 🚀 How to Run (Step by Step)

**Before you start:** make sure Python 3 is installed. Check with `python --version`.

### 1. Download the project
```bash
git clone https://github.com/saptarsijana8/Datheon_Python_FastAPI_Backend_Development_Internship.git
cd Datheon_Python_FastAPI_Backend_Development_Internship/Task-1
```

### 2. Create a virtual environment
**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```
**Mac / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```
You should now see `(venv)` at the start of your terminal line.

### 3. Install the libraries
```bash
pip install -r requirements.txt
```

### 4. Start the backend (Terminal 1)
```bash
uvicorn app.main:app --reload
```
Leave this terminal running. You should see `Uvicorn running on http://127.0.0.1:8000`.

### 5. Start the frontend (Terminal 2)
Open a **second terminal**, go to the same `Task-1` folder, activate the virtual environment again, then run:
```bash
streamlit run frontend.py
```
The dashboard opens in your browser at **http://localhost:8501**.

> ⚠️ The backend must be running before you use the dashboard. If the sidebar says **"Backend: offline"**, start Terminal 1 first.

### Useful links

| What | Link |
|---|---|
| Dashboard (Streamlit) | http://localhost:8501 |
| Swagger UI (API docs) | http://127.0.0.1:8000/docs |

To stop either app, press `Ctrl + C` in its terminal.

---

## 🖥️ How to Use the Dashboard

Use the sidebar on the left to move between pages.

| Page | What you can do |
|---|---|
| 📊 Dashboard | See totals, the stock chart and low-stock books |
| 📖 All Books | View all books. Search by title, filter by author, set a minimum and maximum price |
| ➕ Add Book | Fill in title, author, price and quantity, then click **Add Book** |
| ✏️ Update Book | Select a book, edit the filled-in form, click **Save Changes** |
| 🗑️ Delete Book | Select a book, tick the confirm box, click **Delete Book** |

If you enter invalid data (for example a negative price), the red message shows exactly what the API rejected.

---

## 🔗 API Endpoints

| Method | URL | What it does | Success code |
|---|---|---|---|
| GET | `/books` | Get all books (supports search and filters) | 200 |
| GET | `/books/{book_id}` | Get one book by ID | 200 |
| POST | `/books` | Add a new book | 201 |
| PUT | `/books/{book_id}` | Update a book | 200 |
| DELETE | `/books/{book_id}` | Delete a book | 200 |

### Search and filters (for `GET /books`)

| Parameter | Meaning | Example |
|---|---|---|
| `title` | Search by title (part of the title is enough) | `/books?title=python` |
| `author` | Filter by author name | `/books?author=james` |
| `min_price` | Show books costing at least this much | `/books?min_price=400` |
| `max_price` | Show books costing at most this much | `/books?max_price=600` |

You can combine them: `/books?title=a&min_price=400&max_price=800`

---

## 🧪 Testing the API in Swagger UI

1. Go to **http://127.0.0.1:8000/docs**
2. Click an endpoint, then **Try it out**
3. Fill in the values or JSON body
4. Click **Execute** and read the **Response body** and **Code**

### Example: Add a book (POST /books)

**Request body**
```json
{
  "title": "Deep Work",
  "author": "Cal Newport",
  "price": 399,
  "quantity": 8
}
```

**Response (201 Created)**
```json
{
  "title": "Deep Work",
  "author": "Cal Newport",
  "price": 399.0,
  "quantity": 8,
  "id": 4
}
```

---

## ✅ Validation Rules

| Field | Rule |
|---|---|
| `title` | Required, cannot be empty or only spaces |
| `author` | Required, cannot be empty or only spaces |
| `price` | Required, must be greater than 0 |
| `quantity` | Required, must be a whole number, 0 or more |

Example error for `"price": -5`:
```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "Input should be greater than 0"
    }
  ]
}
```

---

## ⚠️ HTTP Status Codes

| Code | Meaning | When it happens |
|---|---|---|
| 200 | OK | Request worked |
| 201 | Created | A new book was added |
| 400 | Bad Request | `min_price` is greater than `max_price` |
| 404 | Not Found | No book with that ID exists |
| 422 | Validation Error | The data sent breaks a validation rule |

---

## 📖 Sample Data

The backend starts with 3 books so you can test right away:

| ID | Title | Author | Price (₹) | Quantity |
|---|---|---|---|---|
| 1 | Python Crash Course | Eric Matthes | 599.0 | 10 |
| 2 | Clean Code | Robert Martin | 750.5 | 5 |
| 3 | Atomic Habits | James Clear | 450.0 | 20 |

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `No module named 'app'` | Run the uvicorn command from inside the `Task-1` folder, not from inside `app/` |
| `No module named 'fastapi'` or `'streamlit'` | Activate the virtual environment, then run `pip install -r requirements.txt` |
| `'uvicorn' is not recognized` | Activate the virtual environment, or use `python -m uvicorn app.main:app --reload` |
| `'streamlit' is not recognized` | Activate the virtual environment in the **new** terminal, or use `python -m streamlit run frontend.py` |
| Sidebar shows "Backend: offline" | Start the backend first (Terminal 1) |
| `Address already in use` | Another app is using the port. For the backend use `--port 8001` (and change `BASE_URL` in `frontend.py` to match) |
| Added books disappeared | Data is stored in memory, so restarting the backend resets it to the 3 sample books |

---
