

from typing import Optional, Tuple
import uuid
import argon2
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.constants.constants import AUTH_COLLECTION, JWT_AUD, JWT_ISS, SESSIONS_COLLECTION, USER_LITE_COLLECTION
from app.domain.auth import ClaimRequest, LoginRequest, TokenReply
from app.services.auth import ARGON2_PEPPER_ENV, JWT_SECRET_ENV, _clear_refresh_cookies, _create_session, _now, _ratelimit, _read_refresh_cookies, _revoke_all_user_sessions, _revoke_session, _verify_refresh
from app.services.database import get_database


router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer(auto_error=False)

USER_COLLECTION = USER_LITE_COLLECTION

@router.post("/guest", response_model=TokenReply)
async def guest(req: Request, resp: Response):
    # one guest per call (idempotency left to client)
    db = await get_database()
    user_id = str(uuid.uuid4())
    username = f"guest_{user_id}"
    await db[AUTH_COLLECTION].insert_one({
        "_id": user_id,
        "username": username,
        "created_at": _now(),
        "auth": {"type": "guest"},
    })
    return await _create_session(db, user_id, username, req, resp)

@router.post("/login", response_model=TokenReply)
async def login(req: Request, resp: Response, body: LoginRequest):
    await _ratelimit(f"rl:login:{req.client.host}", limit=20, window_sec=60)
    db = await get_database()
    user = await db[AUTH_COLLECTION].find_one({"email": body.email})
    if not user or not user.get("password_hash") or not argon2.verify_password(body.password + ARGON2_PEPPER_ENV, user["password_hash"]):
        raise HTTPException(status_code=401, detail="invalid_credentials")
    return await _create_session(db, user["_id"], user["username"], req, resp)

@router.post("/claim", response_model=TokenReply)
async def claim(req: Request, resp: Response, body: ClaimRequest, creds: HTTPAuthorizationCredentials | None = Depends(bearer)):
    await _ratelimit(f"rl:claim:{req.client.host}", limit=10, window_sec=60)
    if not creds:
        raise HTTPException(status_code=401, detail="auth_required")
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET_ENV, algorithms=["HS256"], audience=JWT_AUD, issuer=JWT_ISS)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid_token")

    db = await get_database()
    if await db[AUTH_COLLECTION].find_one({"email": body.email}):
        raise HTTPException(status_code=409, detail="email_in_use")

    # upgrade current user
    await db[AUTH_COLLECTION].update_one(
        {"_id": payload["sub"]},
        {"$set": {
            "email": body.email,
            "username": body.username,
            "password_hash": argon2.hash_password(body.password + ARGON2_PEPPER_ENV),
            "auth.type": "password",
            "auth.upgraded_at": _now(),
        }}
    )
    # rotate session: revoke old, mint new
    await _revoke_session(db, payload["sid"])
    return await _create_session(db, payload["sub"], payload["username"], req, resp)

@router.post("/refresh", response_model=TokenReply)
async def refresh(req: Request, resp: Response):
    db = await get_database()
    sid, rtok = _read_refresh_cookies(req)
    if not sid or not rtok:
        raise HTTPException(status_code=401, detail="no_refresh")

    sess = await db[SESSIONS_COLLECTION].find_one({"_id": sid})
    if not sess:
        # Unknown sid → generic 401; client will re-guest
        raise HTTPException(status_code=401, detail="bad_refresh")

    # Expired or missing?
    if sess.get("expires_at") and sess["expires_at"] < _now():
        await _revoke_session(db, sid)
        raise HTTPException(status_code=401, detail="expired")

    # If revoked, but token verifies → refresh token reuse (replay)
    if sess.get("revoked", False):
        if _verify_refresh(rtok, sess.get("refresh_hash", "")):
            await _revoke_all_user_sessions(db, sess["user_id"])
        raise HTTPException(status_code=401, detail="revoked")

    # Validate refresh token -> rotate
    if not _verify_refresh(rtok, sess.get("refresh_hash", "")):
        raise HTTPException(status_code=401, detail="bad_refresh")

    # Rotate: revoke old, mint new
    await _revoke_session(db, sid)
    return await _create_session(db, sess["user_id"], sess["username"], req, resp)

@router.post("/logout")
async def logout(req: Request, resp: Response, creds: HTTPAuthorizationCredentials | None = Depends(bearer)):
    # Best effort; clear cookies either way
    _clear_refresh_cookies(resp)
    if not creds:
        return {"ok": True}
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET_ENV, algorithms=["HS256"], audience=JWT_AUD, issuer=JWT_ISS)
    except Exception:
        return {"ok": True}
    db = await get_database()
    await _revoke_session(db, payload["sid"])
    return {"ok": True}

# Optional: whoami
@router.get("/me")
async def me(creds: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if not creds:
        raise HTTPException(status_code=401, detail="no_token")
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET_ENV, algorithms=["HS256"], audience=JWT_AUD, issuer=JWT_ISS)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid_token")
    return {"user_id": payload["sub"], "username": payload["username"], "sid": payload["sid"]}

