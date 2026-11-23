from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from dependencies import get_current_user, require_admin
from models import User
from schemas import Token, UserPublic, UserRegister
from security import create_access_token, get_password_hash, verify_password

# Create tables on startup (fine for a mini-project).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Authentication & RBAC with JWT")


@app.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    # 409 on duplicate username OR email
    existing = (
        db.query(User)
        .filter(or_(User.username == payload.username, User.email == payload.email))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role="user",          # public registration is ALWAYS "user"
        is_active=True,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Race condition safety net
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )
    db.refresh(user)
    return user


@app.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2PasswordRequestForm uses "username" field; we allow username OR email.
    identifier = form_data.username
    user = (
        db.query(User)
        .filter(or_(User.username == identifier, User.email == identifier))
        .first()
    )

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    token = create_access_token(user.id)
    return Token(access_token=token, token_type="bearer")


@app.get("/users/me", response_model=UserPublic)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}, you have accessed a protected route."}


@app.get("/admin")
def admin_only(current_user: User = Depends(require_admin)):
    return {"message": f"Welcome admin {current_user.username}."}


@app.get("/admin/users", response_model=list[UserPublic])
def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.id).all()
