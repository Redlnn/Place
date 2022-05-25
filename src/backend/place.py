#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import dirname, exists, join

import cv2
import numpy as np
from loguru import logger

PLACE_IMAGE_PATH = join(dirname(__file__), 'data', 'place.png')
PLACE_BG_PATH = join(dirname(__file__), 'data', 'place_bg.png')

Mat = np.ndarray[int, np.dtype[np.generic]]

if not exists(PLACE_IMAGE_PATH):
    place_img = np.ones((720, 1280, 3), np.uint8) * 255
    cv2.imwrite(PLACE_IMAGE_PATH, place_img)
else:
    place_img = cv2.imread(PLACE_IMAGE_PATH)


def draw_pixel(x: int, y: int, color: list[int]):
    """画一个像素

    Args:
        x (int): 横坐标
        y (int): 纵坐标
        color (list[int]): RGB 颜色，如：[255, 0, 0]
    """
    color = color.copy()
    color.reverse()
    place_img[y, x] = color
    cv2.imwrite(PLACE_IMAGE_PATH, place_img)


def get_full_image() -> Mat:
    """获取全图"""
    return place_img


def get_image_area(x: int, y: int, w: int = 0, h: int = 0) -> Mat:
    """获取一个区域的图片"""
    if w and h:
        raise ValueError('不可同时输入宽和高')
    elif not w and not h:
        raise ValueError('必须输入宽或高')
    if w:
        if x + w > 1280:
            raise ValueError('超出图像范围')
        h = int(w / 16 * 9)
    elif h:
        if y + h > 720:
            raise ValueError('超出图像范围')
        w = int(h / 9 * 16)
    return place_img[y : y + h, x : x + w]


def get_place(img: Mat) -> Mat:
    """获取画板和色盘"""
    bg = cv2.imread(PLACE_BG_PATH)
    x = 234
    y = 199
    if img.shape != (720, 1280, 3):
        img = cv2.resize(img, (1280, 720), interpolation=cv2.INTER_NEAREST)
    bg[y : y + 720, x : x + 1280] = img
    return bg
