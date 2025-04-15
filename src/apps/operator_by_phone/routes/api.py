# apps/operator_by_phone/routes/api.py
from django.urls import path

from apps.operator_by_phone.controllers import api

urlpatterns = [
    path('operator_by_phone/', api.operator_by_phone, name='operator_by_phone_api'),
]
