# apps/operator_by_phone/models.py
from django.db.models import CharField, BigIntegerField, Model, Index, TextField


class PhoneRange(Model):
    code = CharField(max_length=5, db_index=True)
    range_start = BigIntegerField(db_index=True)
    range_end = BigIntegerField(db_index=True)
    capacity = BigIntegerField(null=True, blank=True)
    operator = CharField(max_length=255)
    region = TextField(max_length=500)
    territory = TextField(max_length=500)
    inn = CharField(max_length=20)

    def __str__(self):
        return f'{self.code} [{self.range_start}-{self.range_end}] {self.operator}'

    class Meta:
        indexes = [Index(fields=['code', 'range_start', 'range_end'])]
