from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..auth import authenticate_user, create_token, get_current_user, register_user
from ..database import get_db
from ..models import User
from ..schemas import Token, UserIn, UserOut

router = APIRouter(prefix='/auth', tags=['auth'])

dbSession = Annotated[Session, Depends(get_db)]

@router.post('/register', response_model=UserOut)
def register(user_info: UserIn, db: dbSession):
    user = register_user(user_info, db)
    return user

@router.post('/login', response_model=Token)
def login(user_info: Annotated[OAuth2PasswordRequestForm, Depends()], db: dbSession):
    credential_exception = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    email = user_info.username
    password = user_info.password
    if not authenticate_user(email, password, db):
        raise credential_exception
    access_token_str = create_token({'sub': email}, exp_delta=timedelta(minutes=60))
    token = Token(access_token=access_token_str, token_type='bearer')
    return token

@router.get('/me', response_model=UserOut)
def get_user(user: Annotated[User, Depends(get_current_user)]):
    return user