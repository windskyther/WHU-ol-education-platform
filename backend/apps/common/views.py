from django.utils import timezone
from rest_framework.decorators import api_view

from apps.common.responses import api_response


@api_view(["GET"])
def health_check(request):
    return api_response({"status": "ok", "time": timezone.now().isoformat()})
