# apps/operator_by_phone/admin.py
from django.contrib import admin

from apps.operator_by_phone.models import PhoneRange


@admin.register(PhoneRange)
class PhoneRangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'range_start', 'range_end', 'operator', 'region')
    search_fields = ('code', 'operator', 'region')
