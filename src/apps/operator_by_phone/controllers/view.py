from django.shortcuts import render

from apps.operator_by_phone.forms import PhoneCheckForm
from apps.operator_by_phone.models import PhoneRange
from apps.operator_by_phone.utils.base import normalize_phone_number


def operator_by_phone(request):
    template_name = 'operator_by_phone/operator_by_phone_form.html'
    context = {}
    form = PhoneCheckForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            norm_number = normalize_phone_number(phone_number)
            if len(norm_number) != 11 or not norm_number.startswith('7'):
                context['error'] = 'Неправильный формат номера (нужен 11-значный, начинающийся с 7).'
            else:
                code = norm_number[1:4]
                subscriber_part = int(norm_number[4:])

                phone_range = PhoneRange.objects.filter(
                    code=code,
                    range_start__lte=subscriber_part,
                    range_end__gte=subscriber_part
                ).first()

                if phone_range:
                    context['phone'] = norm_number
                    context['operator'] = phone_range.operator
                    context['region'] = phone_range.region
                else:
                    context['phone'] = norm_number
                    context['error'] = 'Не удалось найти данные о данном номере.'

    context['form'] = form
    return render(request, template_name, context)
