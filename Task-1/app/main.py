# main.py
# This is the main file. It creates the FastAPI app and defines all endpoints.

from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query

from app.data import books, generate_id
from app.schemas import BookCreate, BookResponse

app = FastAPI(
    title="BookStore API",
    description="A simple REST API to manage books using FastAPI and Pydantic",
    version="1.0.0",
)


@app.get("/")
def home():
    return {"message": "Welcome to the BookStore API. Visit /docs to try it out."}


# ---------- GET all books (with search and filters) ----------
@app.get("/books", response_model=List[BookResponse], tags=["Books"])
def get_all_books(
    title: Optional[str] = Query(None, description="Search books by title"),
    author: Optional[str] = Query(None, description="Filter books by author"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
):
    # min_price should not be bigger than max_price
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")

    result = list(books.values())

    if title:
        result = [b for b in result if title.lower() in b["title"].lower()]

    if author:
        result = [b for b in result if author.lower() in b["author"].lower()]

    if min_price is not None:
        result = [b for b in result if b["price"] >= min_price]

    if max_price is not None:
        result = [b for b in result if b["price"] <= max_price]

    return result


# ---------- GET one book by id ----------
@app.get("/books/{book_id}", response_model=BookResponse, tags=["Books"])
def get_book(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    return books[book_id]


# ---------- POST: add a new book ----------
@app.post("/books", response_model=BookResponse, status_code=201, tags=["Books"])
def add_book(book: BookCreate):
    new_id = generate_id()
    new_book = book.model_dump()   # convert Pydantic object to dictionary
    new_book["id"] = new_id
    books[new_id] = new_book
    return new_book


# ---------- PUT: update an existing book ----------
@app.put("/books/{book_id}", response_model=BookResponse, tags=["Books"])
def update_book(book_id: int, book: BookCreate):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")

    updated_book = book.model_dump()
    updated_book["id"] = book_id
    books[book_id] = updated_book
    return updated_book


# ---------- DELETE: remove a book ----------
@app.delete("/books/{book_id}", tags=["Books"])
def delete_book(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")

    deleted_book = books.pop(book_id)
    return {"message": f"Book '{deleted_book['title']}' deleted successfully"}