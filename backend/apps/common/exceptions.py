from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


class BusinessError(Exception):
    def __init__(self, code=4000, message="business error", http_status=status.HTTP_400_BAD_REQUEST, data=None):
        self.code = code
        self.message = message
        self.http_status = http_status
        self.data = data
        super().__init__(message)


def custom_exception_handler(exc, context):
    if isinstance(exc, BusinessError):
        return Response(
            {"code": exc.code, "message": exc.message, "data": exc.data},
            status=exc.http_status,
        )

    response = exception_handler(exc, context)
    if response is None:
        return Response(
            {"code": 5000, "message": "server error", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    code_map = {
        400: 4000,
        401: 4001,
        403: 4003,
        404: 4040,
        409: 4090,
    }
    message = response.data
    if isinstance(response.data, dict):
        message = response.data.get("detail") or response.data
    response.data = {
        "code": code_map.get(response.status_code, 5000 if response.status_code >= 500 else 4000),
        "message": message,
        "data": None,
    }
    return response
