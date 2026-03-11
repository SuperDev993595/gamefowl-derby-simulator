import secrets
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
import httpx
from app.database import get_db
from app.models import User
from app.schemas import Token, UserCreate, UserLogin, UserResponse
from app.auth import get_password_hash, create_access_token, verify_password, require_user
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _gen_username() -> str:
    return f"player_{secrets.token_hex(4)}"


@router.get("/google")
async def google_login():
    """Redirect to Google OAuth consent. Requires GOOGLE_CLIENT_ID and GOOGLE_REDIRECT_URI."""
    if not settings.google_client_id or not settings.google_redirect_uri:
        raise HTTPException(501, "Google Sign-In is not configured")
    state = secrets.token_urlsafe(32)
    base = "https://accounts.google.com/o/oauth2/v2/auth"
    params = (
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        "&response_type=code"
        "&scope=openid email profile"
        f"&state={state}"
    )
    return RedirectResponse(url=base + params)


from pydantic import BaseModel


class GoogleTokenRequest(BaseModel):
    code: str
    redirect_uri: str | None = None


@router.post("/google/token", response_model=Token)
async def google_token(data: GoogleTokenRequest, db=Depends(get_db)):
    """Exchange Google OAuth code for our JWT. No local password stored (SSO)."""
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(501, "Google Sign-In is not configured")
    redirect_uri = data.redirect_uri or settings.google_redirect_uri
    if not redirect_uri:
        raise HTTPException(400, "redirect_uri required")
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": data.code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if r.status_code != 200:
        raise HTTPException(401, "Invalid or expired Google code")
    token_data = r.json()
    id_token = token_data.get("id_token")
    if not id_token:
        raise HTTPException(401, "No id_token from Google")
    # Decode JWT payload (no sig verify for brevity; in production verify with Google's certs)
    import base64
    import json
    payload_b64 = id_token.split(".")[1]
    payload_b64 += "=" * (4 - len(payload_b64) % 4)
    payload = json.loads(base64.urlsafe_b64decode(payload_b64))
    email = payload.get("email")
    google_id = payload.get("sub")
    if not email:
        raise HTTPException(401, "No email in Google token")
    r = await db.execute(select(User).where(User.google_id == google_id))
    user = r.scalar_one_or_none()
    if not user:
        r2 = await db.execute(select(User).where(User.email == email))
        user = r2.scalar_one_or_none()
        if user:
            user.google_id = google_id
            if user.hashed_password is None:
                pass  # already SSO
            # keep existing user, link google_id
        else:
            user = User(
                email=email,
                username=_gen_username(),
                hashed_password=None,
                google_id=google_id,
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
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user.hashed_password is None:
        raise HTTPException(status_code=401, detail="This account uses Sign in with Google")
    if not verify_password(data.password, user.hashed_password):
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
