from fastapi import APIRouter, HTTPException, status

from app import crud, schemas
from app.database import DbSession

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
)
async def create_user(data: schemas.UserCreate, db: DbSession):
    """Create a user. The password is hashed before storage and never returned."""
    try:
        return await crud.create_user(db, data)
    except crud.DuplicateEmailError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "A user with this email already exists."
        )


@router.get("/", response_model=list[schemas.UserResponse], summary="Get all users")
async def list_users(db: DbSession):
    return await crud.get_users(db)


@router.get(
    "/{user_id}",
    response_model=schemas.UserWithNotes,
    summary="Get a user (with their notes)",
)
async def get_user(user_id: int, db: DbSession):
    """Returns the user and all of their notes, loaded through the ORM relationship."""
    user = await crud.get_user_with_notes(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"User {user_id} not found.")
    return user


@router.get(
    "/{user_id}/notes",
    response_model=list[schemas.NoteResponse],
    summary="Get the notes of a user",
)
async def list_user_notes(user_id: int, db: DbSession):
    if await crud.get_user(db, user_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"User {user_id} not found.")
    return await crud.get_notes_by_user(db, user_id)
