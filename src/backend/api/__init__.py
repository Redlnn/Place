#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# sourcery skip: remove-duplicate-dict-key

from io import BytesIO
from time import time
from typing import Any, Callable

import cv2
from database import Database
from database.models import Draw
from fastapi import HTTPException, Security
from fastapi.responses import ORJSONResponse, StreamingResponse
from oauth2 import get_current_user
from oauth2.models import Bot
from place import draw_pixel as draw_pixel_place
from place import get_full_image as get_full_image_place
from place import get_image_area as get_image_area_place
from place import get_place
from pydantic import BaseModel
from starlette.requests import Request

from .ws_manager import manager


class GeneralResponse(BaseModel):
    code: int
    message: str


class Route(BaseModel):
    path: str
    methods: list[str] | None
    endpoint: Callable
    response_model: Any | None = None
    limit: str | None = None
    kwargs: dict = {}


COLOR_MAP = {
    'a1': [0, 0, 0],
    'a2': [79, 80, 80],
    'a3': [108, 0, 20],
    'a4': [190, 0, 54],
    'a5': [255, 168, 0],
    'a6': [255, 248, 184],
    'a7': [0, 204, 119],
    'a8': [0, 116, 110],
    'a9': [0, 204, 192],
    'a10': [51, 143, 234],
    'a11': [71, 56, 193],
    'a12': [147, 179, 255],
    'a13': [180, 72, 192],
    'a14': [222, 6, 126],
    'a15': [255, 152, 170],
    'a16': [155, 104, 34],
    'b1': [255, 255, 255],
    'b2': [136, 140, 143],
    'b3': [212, 215, 217],
    'b4': [255, 67, 0],
    'b5': [255, 214, 50],
    'b6': [0, 163, 103],
    'b7': [125, 237, 85],
    'b8': [0, 158, 170],
    'b9': [32, 78, 164],
    'b10': [79, 233, 244],
    'b11': [105, 91, 255],
    'b12': [128, 25, 159],
    'b13': [228, 171, 255],
    'b14': [255, 53, 128],
    'b15': [108, 70, 44],
    'b16': [255, 180, 111],
}

routes: list[Route] = []


async def draw_pixel(
    request: Request, group: str, user: str, x: int, y: int, color: str, bot: Bot = Security(get_current_user)
):
    """画一个像素"""
    # sourcery skip: raise-from-previous-error
    if color not in COLOR_MAP:
        raise HTTPException(403, '无效的颜色代码')

    result = await Database.add(
        Draw(
            bot_id=bot.botid,
            group_id=group,
            member_id=user,
            timestamp=str(int(time() * 1000)),
            x=x,
            y=y,
            color=color,
        )
    )
    if not result:
        raise HTTPException(500, GeneralResponse(code=500, message='写入数据库错误').json())

    try:
        draw_pixel_place(x, y, COLOR_MAP[color])
    except Exception as e:
        raise HTTPException(500, GeneralResponse(code=500, message=str(e)).json())

    color_list = COLOR_MAP[color]
    await manager.broadcast(
        '{' + f'"x": {x}, "y": {y}, "color": [{color_list[0]}, {color_list[1]}, {color_list[2]}]' + '}'
    )
    return GeneralResponse(code=200, message='success')


async def get_full_image(request: Request):
    """获得全图"""
    # sourcery skip: raise-from-previous-error
    try:
        res, im_png = cv2.imencode(".png", get_full_image_place())
    except Exception as e:
        raise HTTPException(500, GeneralResponse(code=500, message=str(e)).json())
    else:
        return StreamingResponse(BytesIO(im_png.tobytes()), media_type="image/png")


async def get_image_area(request: Request, x: int, y: int, width: int):
    """获得区域图"""
    # sourcery skip: raise-from-previous-error
    try:
        res, im_png = cv2.imencode(".png", get_image_area_place(x, y, width))
    except Exception as e:
        raise HTTPException(500, GeneralResponse(code=500, message=str(e)).json())
    else:
        return StreamingResponse(BytesIO(im_png.tobytes()), media_type="image/png")


async def get_place_image(request: Request):
    """获得全图+画板"""
    # sourcery skip: raise-from-previous-error
    try:
        res, im_png = cv2.imencode(".png", get_place(get_full_image_place()))
    except Exception as e:
        raise HTTPException(500, GeneralResponse(code=500, message=str(e)).json())
    else:
        return StreamingResponse(BytesIO(im_png.tobytes()), media_type="image/png")


async def get_place_area_image(request: Request, x: int, y: int, width: int):
    """获得区域图+画板"""
    # sourcery skip: raise-from-previous-error
    try:
        res, im_png = cv2.imencode(".png", get_place(get_image_area_place(x, y, width)))
    except Exception as e:
        raise HTTPException(500, GeneralResponse(code=500, message=str(e)).json())
    else:
        return StreamingResponse(BytesIO(im_png.tobytes()), media_type="image/png")


routes.append(
    Route(
        path='/api/draw_pixel',
        methods=['POST'],
        endpoint=draw_pixel,
        response_model=GeneralResponse,
        **{'response_class': ORJSONResponse},
    )
)
routes.append(Route(path='/api/get_full_image', methods=['GET'], endpoint=get_full_image, limit='2/minute'))
routes.append(Route(path='/api/get_image_area', methods=['POST'], endpoint=get_image_area, limit='2/minute'))
routes.append(Route(path='/api/get_place_image', methods=['GET'], endpoint=get_place_image, limit='2/minute'))
routes.append(
    Route(path='/api/get_place_area_image', methods=['POST'], endpoint=get_place_area_image, limit='2/minute')
)
