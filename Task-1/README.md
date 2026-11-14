# 📚 BookStore REST API

A simple REST API for managing a bookstore, built with **Python, FastAPI and Pydantic**.
You can add, view, update, delete, search and filter books, and test everything in your browser using **Swagger UI**. No database or extra setup is needed.

---

## ✨ Features

- View all books, or one book by its ID
- Add a new book
- Update an existing book
- Delete a book
- Search books by title
- Filter books by author
- Filter books by minimum and maximum price
- Input validation (no empty titles, no negative prices, no invalid quantities)
- Clear error messages with proper HTTP status codes
- Automatic interactive documentation (Swagger UI)

---

## 🛠️ Technologies Used

| Technology | Why it is used |
|---|---|
| **Python 3** | Programming language |
| **FastAPI** | Framework for building the API |
| **Pydantic** | Validates the data sent to the API |
| **Uvicorn** | Server that runs the app |

---

## 📁 Project Structure

```
Task-1/
├── app/
│   ├── __init__.py     # Makes "app" a Python package
│   ├── main.py         # All API endpoints
│   ├── schemas.py      # Pydantic models (data validation rules)
│   └── data.py         # Book storage (a Python dictionary)
├── requirements.txt    # Libraries to install
└── README.md           # This file
```

---

## 🚀 How to Run (Step by Step)

**Before you start:** make sure Python 3 is installed. Check with `python --version`.

### 1. Download the project
```bash
git clone  https://github.com/saptarsijana8/Datheon_Python_FastAPI_Backend_Development_Internship.git
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

### 4. Start the server
```bash
uvicorn app.main:app --reload
```
When it works, you will see:
```
Uvicorn running on http://127.0.0.1:8000
```

### 5. Open Swagger UI
Open this link in your browser:

👉 **http://127.0.0.1:8000/docs**

You can now try every endpoint right from that page. To stop the server, press `Ctrl + C` in the terminal.

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

## 🧪 How to Test in Swagger UI

1. Go to **http://127.0.0.1:8000/docs**
2. Click an endpoint to open it
3. Click **Try it out**
4. Fill in the values (or JSON body)
5. Click **Execute**
6. See the result under **Response body** and **Code**

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

### Example: Update a book (PUT /books/4)

**Request body**
```json
{
  "title": "Deep Work",
  "author": "Cal Newport",
  "price": 450,
  "quantity": 8
}
```
**Response (200 OK)** shows the book with the new price.

### Example: Delete a book (DELETE /books/4)

**Response (200 OK)**
```json
{
  "message": "Book 'Deep Work' deleted successfully"
}
```

---

## ✅ Validation Rules

Every book must follow these rules:

| Field | Rule |
|---|---|
| `title` | Required, cannot be empty or only spaces |
| `author` | Required, cannot be empty or only spaces |
| `price` | Required, must be greater than 0 |
| `quantity` | Required, must be a whole number, 0 or more |

If a rule is broken, the API returns **422** with a message explaining what is wrong. For example, sending `"price": -5` returns:
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

Example 404 response:
```json
{
  "detail": "Book not found"
}
```

---

## 📖 Sample Data

The app starts with 3 books so you can test right away:

| ID | Title | Author | Price | Quantity |
|---|---|---|---|---|
| 1 | Python Crash Course | Eric Matthes | 599.0 | 10 |
| 2 | Clean Code | Robert Martin | 750.5 | 5 |
| 3 | Atomic Habits | James Clear | 450.0 | 20 |

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `No module named 'app'` | Run the command from the `bookstore-api` folder, not from inside `app/` |
| `No module named 'fastapi'` | Activate the virtual environment, then run `pip install -r requirements.txt` |
| `'uvicorn' is not recognized` | Activate the virtual environment, or use `python -m uvicorn app.main:app --reload` |
| `Address already in use` | Another app is using port 8000. Use `uvicorn app.main:app --reload --port 8001` |

---

## 📝 Notes and Limitations

- Books are stored **in memory** (a Python dictionary), so all changes are lost when the server restarts.
- There is no login or authentication.

## 💡 Future Improvements

- Store books in a real database (SQLite or MySQL)
- Add user login
- Add pagination for large book lists

---

