import os
import bcrypt
import jwt
from fastapi import Depends, HTTPException, APIRouter, Response
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from starlette.responses import JSONResponse

from userservice.model import User, UserDetails
from userservice.repository import UserRepositoryService

# Secret key and JWT setup
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
ALGORITHM = "HS256"
JWT_EXPIRATION_TIME = 86400  # 1day

ROUTE_PREFIX = "/auth"

router = APIRouter(prefix=ROUTE_PREFIX, tags=["user-service"])

# OAuth2PasswordBearer is used for token extraction in headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

user_db = UserRepositoryService()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_jwt_token(username: str, role: str):
    expiration = datetime.now() + timedelta(seconds=JWT_EXPIRATION_TIME)
    payload = {
        "sub": username,
        "role": role,
        "exp": expiration
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login")
def login_for_access_token(user_details: UserDetails):
    user = user_db.get_user(user_details.username)
    if not user or not verify_password(user_details.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_jwt_token(user_details.username, user.get("role", "USER"))
    return {"access_token": access_token, "token_type": "bearer", "role": user.get("role", "USER"), "user_id": str(user.get("_id"))}
