# schemas.py
# Pydantic models. They describe how book data should look
# and automatically validate the data sent by the user.

from pydantic import BaseModel, Field, field_validator


class BookCreate(BaseModel):
    """Data the user sends when adding or updating a book (no id)."""
    title: str
    author: str
    price: float = Field(gt=0, description="Price must be greater than 0")
    quantity: int = Field(ge=0, description="Quantity cannot be negative")

    # Check that title and author are not empty or just spaces
    @field_validator("title", "author")
    @classmethod
    def check_not_empty(cls, value):
        if value.strip() == "":
            raise ValueError("This field cannot be empty")
        return value.strip()


class BookResponse(BookCreate):
    """Data we send back to the user (same fields + id)."""
    id: int