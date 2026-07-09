from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.common.views import health_check


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/auth/", include("apps.users.auth_urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/", include("apps.courses.urls")),
    path("api/", include("apps.progress.urls")),
    path("api/", include("apps.exams.urls")),
    path("api/", include("apps.qa.urls")),
    path("api/", include("apps.community.urls")),
    path("api/", include("apps.certificates.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
