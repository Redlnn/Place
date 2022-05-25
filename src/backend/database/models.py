#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from sqlmodel import Field, SQLModel

__all__ = ['Draw']


class Draw(SQLModel, table=True):
    __tablename__: str = 'msg_history'
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    bot_id: str = Field(max_length=12, nullable=False, index=True)
    group_id: str = Field(max_length=12, nullable=False, index=True)
    member_id: str = Field(max_length=12, nullable=False, index=True)
    timestamp: str = Field(max_length=15, nullable=False, index=True)
    x: int
    y: int
    color: str = Field(max_length=10, nullable=False, index=True)
