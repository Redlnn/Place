#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from util.better_pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class Bot(BaseModel):
    botid: str
    name: str
    hashed_password: str
    disabled: Optional[bool] = None
