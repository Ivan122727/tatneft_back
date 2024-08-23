import logging

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

log = logging.getLogger(__name__)


async def err_handler(request: Request, exc: Exception):
    log.exception(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "err": f"{exc}"
        }
    )
