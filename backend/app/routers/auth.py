from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import Token, UserCreate, UserLogin, UserResponse
from app.auth import get_password_hash, create_access_token, verify_password, require_user
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _gen_username() -> str:
    import secrets
    return f"player_{secrets.token_hex(4)}"


@router.post("/register", response_model=Token)
async def register(data: UserCreate, db=Depends(get_db)):
    r = await db.execute(select(User).where(User.email == data.email))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    username = _gen_username()
    user = User(
        email=data.email,
        username=username,
        hashed_password=get_password_hash(data.password),
        token_balance=settings.starting_tokens,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=token,
        username=user.username,
        is_admin=user.is_admin,
        token_balance=user.token_balance,
    )


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db=Depends(get_db)):
    r = await db.execute(select(User).where(User.email == data.email))
    user = r.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=token,
        username=user.username,
        is_admin=user.is_admin,
        token_balance=user.token_balance,
    )


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(require_user)):
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        token_balance=user.token_balance,
        is_admin=user.is_admin,
        created_at=user.created_at,
    )
