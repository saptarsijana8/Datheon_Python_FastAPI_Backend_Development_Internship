from fastapi import APIRouter, HTTPException, Response, status

from app import crud, schemas
from app.database import DbSession

router = APIRouter(prefix="/notes", tags=["Notes"])


def note_not_found(note_id: int) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"Note {note_id} not found.")


@router.post(
    "/",
    response_model=schemas.NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note",
)
async def create_note(data: schemas.NoteCreate, db: DbSession):
    """Create a note for an existing user (404 if the user does not exist)."""
    note = await crud.create_note(db, data)
    if note is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"User {data.user_id} not found."
        )
    return note


@router.get("/", response_model=list[schemas.NoteResponse], summary="Get all notes")
async def list_notes(db: DbSession):
    return await crud.get_notes(db)


@router.get("/{note_id}", response_model=schemas.NoteResponse, summary="Get a note")
async def get_note(note_id: int, db: DbSession):
    note = await crud.get_note(db, note_id)
    if note is None:
        raise note_not_found(note_id)
    return note


@router.put("/{note_id}", response_model=schemas.NoteResponse, summary="Update a note")
async def update_note(note_id: int, data: schemas.NoteUpdate, db: DbSession):
    """Update the title and/or content of a note. Send only the fields to change."""
    note = await crud.update_note(db, note_id, data)
    if note is None:
        raise note_not_found(note_id)
    return note


@router.delete(
    "/{note_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a note"
)
async def delete_note(note_id: int, db: DbSession):
    if not await crud.delete_note(db, note_id):
        raise note_not_found(note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
