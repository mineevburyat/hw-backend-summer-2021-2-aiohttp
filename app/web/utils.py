import base64
from typing import Any, Optional
from hashlib import sha256

from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


def json_response(data: Any = None, status: str = "ok") -> Response:
    if data is None:
        data = {}
    return aiohttp_json_response(
        data={
            "status": status,
            "data": data,
        }
    )
    

def error_json_response(http_status: int, status: str = 'error', message: Optional[str] = None,
                        data: Optional[dict] = None):
    if data is None:
        data = {}
    return aiohttp_json_response(
        status=http_status,
        data={
            "status": status,
            "message": str(message),
            "data": data,
        })



def check_basic_auth(raw_credentials: str, email: str, password: str) -> bool:
    credentials = base64.b64decode(raw_credentials).decode()
    parts = credentials.split(':')
    if len(parts) != 2:
        return False
    return parts[0] == email and sha256(parts[1].encode()).hexdigest() == password