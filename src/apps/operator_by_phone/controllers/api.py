from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.operator_by_phone.models import PhoneRange
from apps.operator_by_phone.utils.base import normalize_phone_number


@api_view(('GET', 'POST'))
def operator_by_phone(request):
    """
    --> Номер в формате MSISDN (например 79173453223).
    <-- JSON с оператором и регионом, либо ошибку.
    Пример: GET /api/phone_lookup/?phone_number=79173453223
    """
    phone_number = request.GET.get('phone_number') or request.data.get('phone_number')
    if not phone_number:
        return Response({'error': 'Параметр phone_number не передан'}, status=400)

    norm_number = normalize_phone_number(phone_number)
    if len(norm_number) != 11 or not norm_number.startswith('7'):
        return Response({'error': 'Неверный формат номера'}, status=400)

    code = norm_number[1:4]  # три цифры после 7
    subscriber_part = int(norm_number[4:])  # последние 7 цифр

    phone_range = PhoneRange.objects.filter(
        code=code,
        range_start__lte=subscriber_part,
        range_end__gte=subscriber_part
    ).first()

    if phone_range:
        return Response({
            'phone': norm_number,
            'operator': phone_range.operator,
            'region': phone_range.region
        })
    else:
        return Response({'error': 'Нет информации о данном номере'}, status=404)
