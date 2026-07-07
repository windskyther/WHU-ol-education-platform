from rest_framework.response import Response


def api_response(data=None, message="success", code=0, status=200):
    return Response({"code": code, "message": message, "data": data}, status=status)
