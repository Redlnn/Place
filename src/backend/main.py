#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import traceback
from asyncio import get_running_loop
from pathlib import Path

from api import routes
from api.ws_manager import manager
from database import Database
from fastapi import FastAPI, WebSocket
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from oauth2 import Token, login_for_access_token
from place import save
from slowapi.errors import RateLimitExceeded
from slowapi.extension import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from starlette.websockets import WebSocketDisconnect
from util.log import LoguruHandler, loguru_async_handler, loguru_excepthook
from uvicorn import Config, Server
from websockets.exceptions import ConnectionClosedOK

traceback.print_exception = loguru_excepthook
sys.excepthook = loguru_excepthook

HTML_PATH = Path(__file__).parent / 'html'

with open(HTML_PATH / 'index.html', 'r') as f:
    INDEX_HTML = f.read()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.mount('/static', StaticFiles(directory=HTML_PATH / 'static'), name='static')


@app.get('/', response_class=HTMLResponse)
async def index():
    return INDEX_HTML


@app.on_event('startup')
async def on_start():
    loop = get_running_loop()
    loop.set_exception_handler(loguru_async_handler)

    await Database.init()

    app.add_api_route(path='/login', methods=['POST'], endpoint=login_for_access_token, response_model=Token, response_class=ORJSONResponse)  # type: ignore
    for route in routes:
        app.add_api_route(
            path=route.path,
            methods=route.methods,
            endpoint=limiter.limit(route.limit)(route.endpoint) if route.limit is not None else route.endpoint,
            response_model=route.response_model,
            **route.kwargs,
        )


@app.websocket('/ws')
async def websocket(client: WebSocket):
    await manager.connect(client)
    while True:
        try:
            await client.receive_text()
        except (WebSocketDisconnect, ConnectionClosedOK):
            manager.disconnect(client)
        except RuntimeError:
            break


if __name__ == '__main__':
    server = Server(Config(app, host='localhost', port=8000))
    loggers = ['uvicorn.access', 'uvicorn', 'uvicorn.asgi']
    for _ in loggers:
        logging_logger = logging.getLogger(_)
        for handler in logging_logger.handlers:
            logging_logger.removeHandler(handler)
        logging_logger.addHandler(LoguruHandler())
        logging_logger.setLevel(logging.DEBUG)
    server.run()
