from typing import Any

from fastapi import Request, Response

ALLOWED_ORIGINS = [
    'localhost:5173',
    'localhost:3000',
]


async def cors_middleware(request: Request, call_next: Any) -> Response:
    if request.method == 'OPTIONS':
        rsp = Response()
    else:
        rsp = await call_next(request)

    origin = request.headers.get('origin')
    if origin and any(
        allowed_origin in origin for allowed_origin in ALLOWED_ORIGINS
    ):
        rsp.headers['Access-Control-Allow-Origin'] = origin
        rsp.headers['Access-Control-Allow-Credentials'] = 'true'
        rsp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        rsp.headers['Access-Control-Allow-Methods'] = (
            'GET,POST,OPTIONS,PUT,PATCH,DELETE'
        )
    return rsp
