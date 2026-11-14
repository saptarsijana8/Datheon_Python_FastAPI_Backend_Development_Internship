# data.py
# This file acts as our "database". We store books in a Python dictionary.
# Key = book id, Value = a dictionary with the book details.

books = {
    1: {"id": 1, "title": "Python Crash Course", "author": "Eric Matthes", "price": 599.0, "quantity": 10},
    2: {"id": 2, "title": "Clean Code", "author": "Robert Martin", "price": 750.5, "quantity": 5},
    3: {"id": 3, "title": "Atomic Habits", "author": "James Clear", "price": 450.0, "quantity": 20},
}

# The id that will be given to the next book we add
next_id = 4


def generate_id():
    """Return a new unique id and move the counter forward."""
    global next_id
    new_id = next_id
    next_id += 1
    return new_id