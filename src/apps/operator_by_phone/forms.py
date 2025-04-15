# apps/operator_by_phone/forms.py
from django.forms import Form, CharField


class PhoneCheckForm(Form):
    """
    Форма для ввода номера телефона в формате MSISDN (например 79173453223).
    """
    phone_number = CharField(label='Номер телефона', max_length=15)
