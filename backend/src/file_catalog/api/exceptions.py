from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from file_catalog.exceptions import FileNotFound, RateLimitExceeded


async def file_not_found_handler(
    request: Request, exc: FileNotFound
) -> JSONResponse:
    return JSONResponse(
        content={'detail': str(exc)},
        status_code=404,
    )


async def rate_limit_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    headers = {'Retry-After': str(exc.retry_after)}
    status_code = (
        status.HTTP_403_FORBIDDEN
        if exc.blocked
        else status.HTTP_429_TOO_MANY_REQUESTS
    )
    return JSONResponse(
        content={'detail': exc.args[0], 'retry_after': exc.retry_after},
        status_code=status_code,
        headers=headers,
    )


def setup_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(FileNotFound, file_not_found_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)  # type: ignore[arg-type]
