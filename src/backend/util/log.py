#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from types import TracebackType
from typing import Type

from loguru import logger


def loguru_excepthook(cls: Type[BaseException], val: BaseException, tb: TracebackType, *_, **__):
    logger.opt(exception=(cls, val, tb)).error("Exception:")


def loguru_async_handler(_, ctx: dict):
    if "exception" in ctx:
        logger.opt(exception=ctx["exception"]).error("Exception:")
    else:
        logger.error(f"Exception: {ctx}")


class LoguruHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
