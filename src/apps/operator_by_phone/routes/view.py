# apps/operator_by_phone/routes/view.py
from django.urls import path

from apps.operator_by_phone.controllers import view

urlpatterns = [
    path('operator_by_phone/', view.operator_by_phone, name='operator_by_phone_view'),
]
