# core/controllers/health.py
import logging

from django.db import connections
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_503_SERVICE_UNAVAILABLE
)

log = logging.getLogger('console')


@api_view(('GET', 'HEAD'))
@permission_classes((AllowAny,))
def health(_request) -> Response:
    try:
        connections['default'].cursor()
    except Exception as e:
        return Response(f'Database is dead', HTTP_503_SERVICE_UNAVAILABLE)

    return Response('ok')
