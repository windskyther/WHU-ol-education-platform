from django.urls import path

from apps.certificates.views import CertificateDetailView, MyCertificateListView

urlpatterns = [
    path("certificates/mine/", MyCertificateListView.as_view(), name="my-certificates"),
    path("certificates/<str:cert_no>/", CertificateDetailView.as_view(), name="certificate-detail"),
]
