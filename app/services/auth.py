import uuid, secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from passlib.hash import argon2
from fastapi import Depends, HTTPException, Request, Response

from app.core.redis_queue import get_redis
from app.domain.auth import TokenReply
from app.services.database import get_database
from app.constants.constants import (
    SESSIONS_COLLECTION,
    JWT_ISS, JWT_AUD,
    REFRESH_COOKIE_NAME, SESSION_COOKIE_NAME,
)

from app.core.config import JWT_SECRET_ENV, ARGON2_PEPPER_ENV, ACCESS_TTL_MIN, REFRESH_TTL_DAYS

bearer = HTTPBearer(auto_error=False)

# --- Redis (rate limiting) ---
_r = get_redis()

# --- Helpers ---
def _now() -> datetime:
    return datetime.now()  # keep consistent with rest of code

def _hash_refresh(token: str) -> str:
    return argon2.hash(token + ARGON2_PEPPER_ENV)

def _verify_refresh(token: str, hashed: str) -> bool:
    try:
        return argon2.verify(token + ARGON2_PEPPER_ENV, hashed)
    except Exception:
        return False
    
def _mint_access(session_id: str, user_id: str, username: str) -> str:
    exp = _now() + timedelta(minutes=ACCESS_TTL_MIN)
    payload = {
        "iss": JWT_ISS,
        "aud": JWT_AUD,
        "sub": user_id,
        "sid": session_id,
        "username": username,
        "iat": int(_now().timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET_ENV, algorithm="HS256")


def _set_refresh_cookies(resp: Response, session_id: str, refresh_token: str):
    # Bind refresh to its session id: two cookies scoped to /auth/refresh only
    cookie_params = dict(
        httponly=True, secure=True, samesite="Lax",
        path="/auth/refresh", max_age=REFRESH_TTL_DAYS * 86400
    )
    resp.set_cookie(key=SESSION_COOKIE_NAME, value=session_id, **cookie_params)
    resp.set_cookie(key=REFRESH_COOKIE_NAME, value=refresh_token, **cookie_params)

def _clear_refresh_cookies(resp: Response):
    for name in (SESSION_COOKIE_NAME, REFRESH_COOKIE_NAME):
        resp.set_cookie(key=name, value="", path="/auth/refresh", max_age=0)

async def _create_session(db, user_id: str, username: str, req: Request, resp: Response) -> TokenReply:
    sid = str(uuid.uuid4())
    refresh = secrets.token_urlsafe(48)
    await db[SESSIONS_COLLECTION].insert_one({
        "_id": sid,
        "user_id": user_id,
        "username": username,
        "refresh_hash": _hash_refresh(refresh),
        "created_at": _now(),
        "last_used": None,
        "expires_at": _now() + timedelta(days=REFRESH_TTL_DAYS),
        "revoked": False,
        "reused_at": None,
        "ua": req.headers.get("user-agent"),
        "ip": (req.client.host if req.client else None),
    })
    _set_refresh_cookies(resp, sid, refresh)
    return TokenReply(access_token=_mint_access(sid, user_id, username), username=username, expires_in=(ACCESS_TTL_MIN * 60))

async def _revoke_session(db, sid: str, *, reused: bool = False):
    fields = {"revoked": True}
    if reused:
        fields["reused_at"] = _now()
    await db[SESSIONS_COLLECTION].update_one({"_id": sid}, {"$set": fields})

async def _revoke_all_user_sessions(db, user_id: str):
    await db[SESSIONS_COLLECTION].update_many({"user_id": user_id, "revoked": False},
                                             {"$set": {"revoked": True}})

def _read_refresh_cookies(req: Request) -> Tuple[Optional[str], Optional[str]]:
    return req.cookies.get(SESSION_COOKIE_NAME), req.cookies.get(REFRESH_COOKIE_NAME)

# --- Rate limiting (simple Redis token bucket) ---
async def _ratelimit(key: str, limit: int, window_sec: int):
    # Incr key; on first hit set expiry
    cur = _r.incr(key)
    if cur == 1:
        _r.expire(key, window_sec)
    if cur > limit:
        ttl = _r.ttl(key) or window_sec
        raise HTTPException(status_code=429, detail=f"rate_limited retry_in={ttl}s")
    
    
async def get_current_identity(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> Optional[Tuple[str, str]]:
    if not creds:
        return None
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET_ENV, algorithms=["HS256"], audience=JWT_AUD, issuer=JWT_ISS)
        return (payload["sub"], payload["username"])
    except Exception:
        return None

async def require_auth(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    check_session: bool = True,  # set False if you don't want DB hit per request
):
    """Hard-require a valid access token. Returns (user_id, username, sid)."""
    if not creds:
        raise HTTPException(status_code=401, detail="missing_token")

    try:
        payload = jwt.decode(
            creds.credentials,  # access token
            JWT_SECRET_ENV,
            algorithms=["HS256"],
            audience=JWT_AUD,
            issuer=JWT_ISS,
        )
        user_id = payload["sub"]
        username = payload["username"]
        sid = payload["sid"]
    except Exception:
        raise HTTPException(status_code=401, detail="invalid_token")

    if check_session:
        db = await get_database()
        sess = await db[SESSIONS_COLLECTION].find_one({"_id": sid})
        # Treat missing/revoked/expired as unauthorized
        if not sess or sess.get("revoked"):
            raise HTTPException(status_code=401, detail="session_revoked")
        if sess.get("expires_at") and sess["expires_at"] <= datetime.now():
            raise HTTPException(status_code=401, detail="session_expired")

    return (user_id, username, sid)
    
