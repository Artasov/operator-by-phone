# apps/core/routes/root.py
from django.contrib import admin
from django.urls import path, include

from apps.core.controllers.health import health

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health, name='health'),

    # Operator By Phone
    path('', include('apps.operator_by_phone.routes.view')),
    path('api/v1/', include('apps.operator_by_phone.routes.api')),
]
