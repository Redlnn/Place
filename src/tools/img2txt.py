#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join

import cv2

IMAGE_PATH = join('origin.png')
TXT_PATH = join('target.txt')


def img2txt():
    img = cv2.imread(IMAGE_PATH)
    img = cv2.resize(img, (1280, 720), interpolation=cv2.INTER_LANCZOS4)

    with open(TXT_PATH, 'w') as f:
        for i in range(img.shape[0]):
            for j in img[i, :]:
                r = hex(j[2])[2:]
                g = hex(j[1])[2:]
                b = hex(j[0])[2:]
                f.write(
                    f'#{r if len(r) == 2 else f"0{r}"}{g if len(g) == 2 else f"0{g}"}{b if len(b) == 2 else f"0{b}"},'
                )
            f.write('\n')


if __name__ == '__main__':
    img2txt()
