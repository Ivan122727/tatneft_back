import logging
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from tatneft_back.api import err_handler

from tatneft_back.api.events import on_startup, on_shutdown
from tatneft_back.api.v1.router import api_v1_router
from tatneft_back.core.consts import settings
from tatneft_back.log import setup_logging
from tatneft_back.core.settings import STATIC_DIRPATH

log = logging.getLogger(__name__)


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.api_title,
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/api/openapi.json"
    )
    
    if not os.path.exists(STATIC_DIRPATH):
        os.makedirs(STATIC_DIRPATH)
    app.mount("/static", StaticFiles(directory=STATIC_DIRPATH), name="static")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.add_exception_handler(exc_class_or_status_code=Exception, handler=err_handler)
    app.include_router(api_v1_router, prefix=settings.api_prefix)

    return app
