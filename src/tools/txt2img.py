#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join

import cv2
import numpy as np

TXT_PATH = join('target.txt')


def txt2img(save: bool = False, path: str = 'target.jpg'):
    img = np.zeros((720, 1280, 3), dtype=np.uint8)

    with open(TXT_PATH, 'r') as f:
        data = f.read()

    rows = data.rstrip().rstrip().split('\n')
    for i in range(len(rows)):
        rows[i] = rows[i].rstrip(',')
        cols = rows[i].split(',')
        for j in range(len(cols)):
            hex_color = cols[j]
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:], 16)
            img[i, j] = [b, g, r]
    if save:
        cv2.imwrite(path, img)
    cv2.imshow('img', img)
    cv2.waitKey()


if __name__ == '__main__':
    txt2img()
