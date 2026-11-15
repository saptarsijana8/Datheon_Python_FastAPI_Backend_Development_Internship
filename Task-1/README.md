# BookStore REST API

A simple RESTful API built using **Python, FastAPI, and Pydantic** to manage a collection of books. This project demonstrates CRUD operations, request validation, query filtering, and automatic API documentation.

## Features

- **Get Books:** Retrieve all available books.
- **Get Book by ID:** Retrieve a specific book using its ID.
- **Add Book:** Create a new book entry.
- **Update Book:** Update an existing book.
- **Delete Book:** Remove a book from the collection.
- **Search & Filter:** Filter books by title, author, and price range.
- **Data Validation:** Validate input using Pydantic schemas.
- **API Documentation:** Automatic interactive documentation using Swagger UI.
- **Automated Testing:** Test API endpoints using Pytest.

## Tech Stack

- Python 3.11
- FastAPI
- Pydantic
- Uvicorn
- Pytest
- HTTPX

## Project Structure

```text
Task-1/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   └── data.py
│
├── tests/
│   └── test_main.py
│
├── requirements.txt
├── pytest.ini
└── README.md
```

## Installation & Setup

**1. Clone the repository**

```bash
git clone https://github.com/saptarsijana8/Datheon_Python_FastAPI_Backend_Development_Internship.git
```

**2. Navigate to the project folder**

```bash
cd Datheon_Python_FastAPI_Backend_Development_Internship/Task-1
```

**3. Create and activate a virtual environment**

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

## API Documentation

FastAPI automatically generates interactive API documentation.

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## Run Tests

Execute the following command from the `Task-1` directory:

```bash
python -m pytest -v
```

**Test Results:** All 9 test cases passed successfully.

The tests cover:
- Home endpoint
- Retrieving all books
- Retrieving a book by ID
- Filtering books
- Creating a book
- Invalid input validation
- Book not found handling
- Updating a book
- Deleting a book

## Testing API with Swagger UI

To interact with and test the API manually:

1. Start the FastAPI server.
2. Open `http://127.0.0.1:8000/docs` in your browser.
3. Select an API endpoint.
4. Click **Try it out**.
5. Enter the required parameters or JSON request body.
6. Click **Execute** to view the response.

No separate Swagger installation is required.

## Data Storage

This project currently uses an in-memory Python dictionary for storing book records. Data is reset to its initial state whenever the application restarts. No external database is required.

## Project Objective

To develop a simple RESTful BookStore API using FastAPI and Pydantic, demonstrating backend development fundamentals, CRUD operations, request validation, query filtering, and automated testing.
