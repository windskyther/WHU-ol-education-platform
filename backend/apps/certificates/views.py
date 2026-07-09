from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.certificates.models import Certificate
from apps.certificates.serializers import CertificateSerializer
from apps.common.exceptions import BusinessError
from apps.common.pagination import StandardPagination
from apps.common.permissions import get_user_role
from apps.common.responses import api_response


class MyCertificateListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Certificate.objects.filter(student=request.user).select_related(
            "student", "course", "course__teacher", "exam"
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CertificateSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class CertificateDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, cert_no):
        certificate = Certificate.objects.select_related(
            "student", "course", "course__teacher", "exam"
        ).filter(cert_no=cert_no).first()
        if not certificate:
            raise BusinessError(4040, "CERTIFICATE_NOT_FOUND", status.HTTP_404_NOT_FOUND)

        user = request.user
        role = get_user_role(user)
        is_owner = certificate.student_id == user.id
        is_course_owner = certificate.course.teacher_id == user.id
        if not (is_owner or is_course_owner or role == "admin"):
            raise BusinessError(4003, "CERTIFICATE_ACCESS_DENIED", status.HTTP_403_FORBIDDEN)

        return api_response(CertificateSerializer(certificate, context={"request": request}).data)
