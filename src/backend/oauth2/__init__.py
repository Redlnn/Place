#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import timedelta
from typing import Mapping

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from .models import Bot, Token
from .util import (
    ALGORITHM,
    SECRET_KEY,
    UnauthorizedException,
    authenticate_user,
    create_access_token,
    fake_botid_db,
    get_user,
)

# to get a string like this run:
# openssl rand -hex 32
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

ACCESS_TOKEN_EXPIRE_MINUTES = 120


async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    bot = authenticate_user(form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token_expires = timedelta(seconds=20)
    access_token = create_access_token(data={"sub": bot.botid}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Bot:
    try:
        payload: Mapping = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        botid: str = payload.get("sub", None)
        if botid is None:
            raise UnauthorizedException(detail="无效的用户")
    except JWTError as e:
        raise UnauthorizedException(detail="无效的 Token 或 Token 已过期") from e
    user = get_user(botid=botid)
    if user is None:
        raise UnauthorizedException(detail="无效的用户")
    if user.disabled:
        raise UnauthorizedException(detail="该用户已被禁用")
    return user
