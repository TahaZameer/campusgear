from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from ..models import User
from ..auth import register_user, create_token, authenticate_user, get_current_user
from ..database import get_db
from ..schemas import UserOut, UserIn, Token
from typing import Annotated
from datetime import timedelta

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