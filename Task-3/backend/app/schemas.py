"""Pydantic v2 request and response schemas (kept separate on purpose)."""

from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    model_validator,
)

Username = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=50)]
NoteTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
NoteContent = Annotated[str, Field(max_length=10_000)]


# ---------- Users ----------
class UserCreate(BaseModel):
    username: Username = Field(examples=["alice"])
    email: EmailStr = Field(examples=["alice@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["StrongPass123"])


class UserResponse(BaseModel):
    """Public user data. There is deliberately no password field here."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime


# ---------- Notes ----------
class NoteCreate(BaseModel):
    title: NoteTitle = Field(examples=["Shopping list"])
    content: NoteContent = Field(default="", examples=["Milk, eggs, bread"])
    user_id: int = Field(gt=0, examples=[1])


class NoteUpdate(BaseModel):
    """Partial update: send only the fields you want to change."""

    title: NoteTitle | None = None
    content: NoteContent | None = None

    @model_validator(mode="after")
    def check_fields(self) -> "NoteUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update (title or content).")
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("title cannot be null.")
        if "content" in self.model_fields_set and self.content is None:
            raise ValueError("content cannot be null.")
        return self


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    user_id: int
    created_at: datetime
    updated_at: datetime


class UserWithNotes(UserResponse):
    """A user together with all of their notes (loaded through the ORM relationship)."""

    notes: list[NoteResponse]
