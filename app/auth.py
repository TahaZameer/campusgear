from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import ALGORITHM, SECRET_KEY
from .database import get_db
from .models import User
from .schemas import UserIn

password_hashing = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

DUMMY_HASH = password_hashing.hash('dummypass')

def email_check(email: str, db: Session):
    user = db.scalar(select(User).where(User.email == email))
    return user

def register_user(user: UserIn, db: Session):
    email = str(user.email).strip().lower()
    if email_check(email, db):
        raise HTTPException(status_code=409, detail='email already exists')
    hashed_password = password_hashing.hash(user.password)
    new_user = User(full_name=user.full_name, email=email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def verify_password(password, hashed_pass):
    return password_hashing.verify(password, hashed_pass)

def authenticate_user(email: str, password: str, db: Session):
    user = email_check(email, db)
    if user is None:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_token(data: dict, exp_delta: timedelta | None = None):
    to_encode = data.copy()
    if exp_delta:
        expire = datetime.now(timezone.utc) + exp_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({'exp': expire})
    access_token = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return access_token

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]):
    credential_exception = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        email = payload.get('sub')
        if email is None:
            raise credential_exception
    except InvalidTokenError:
        raise credential_exception
    user = email_check(email, db)
    if user is None:
        raise credential_exception
    return user