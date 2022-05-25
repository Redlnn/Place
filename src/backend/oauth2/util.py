#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext

from .models import Bot

fake_botid_db = {
    '123456': Bot(
        botid='123456',
        name='bot',
        disabled=False,
        hashed_password='$2b$12$nCVsKGQch6NAsOekLgy9VOebs0soRfOazkr4D6Pj8s6fmpllc.6fm',
    ),
}

# to get a string like this run:
# openssl rand -hex 32
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
SECRET_KEY = secrets.token_urlsafe(64)
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UnauthorizedException(HTTPException):
    def __init__(self, detail="Unauthorized", *args, **kwargs):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            *args,
            **kwargs,
        )


def get_user(botid: str) -> Bot | None:
    if botid in fake_botid_db:
        return fake_botid_db[botid]


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, plain_password: str) -> Bot:
    """验证用户名和密码

    Args:
        username(str): 用户名
        plain_password(str): 明文密码
    Returns:
        user(Bot): 用户信息
    """
    user = get_user(username)
    if user is None:
        raise UnauthorizedException(detail="无效的用户名或密码")
    if user.disabled:
        raise UnauthorizedException(detail="该用户已被禁用")
    if not verify_password(plain_password, user.hashed_password):
        raise UnauthorizedException(detail="无效的用户名或密码")
    return user


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = timedelta(minutes=30),
    scopes: list[str] | None = None,
) -> str:
    """创建 JWT Token

    Args:
        data(dict): 包含用户信息的字典. {'sub': user_info}
        expires_delta(Optional[timedelta]): Token 过期时间，默认为 30分钟
        scopes(Optional[list[str]]): Token 授权范围，默认为 None
    Returns:
        token(str): JWT Token
    """
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode["exp"] = expire

    if scopes is not None:
        to_encode["scopes"] = scopes

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
        headers={"typ": "JWT", "alg": ALGORITHM},
    )
