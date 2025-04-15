# operator-by-phone/src/apps/operator_by_phone/tasks.py
import csv
import logging

import requests
from adjango.utils.common import traceback_str
from celery import shared_task
from django.conf import settings
from django.db import transaction, connection

log = logging.getLogger('global')


@shared_task
def update_phone_ranges():
    """
    Ежедневная задача по синхронизации таблицы диапазонов номеров с данными CSV.

    Алгоритм:
      1. Скачиваем CSV-файлы из settings.REGISTER_OF_NUMBERING.
      2. Парсим каждую строку и собираем записи в список.
      3. Группируем записи по уникальному ключу (code, range_start, range_end) —
         таким образом, если для одного кода диапазоны пересекаются или изменились,
         в итоговом наборе окажется именно то, что передаёт CSV как источник правды.
      4. В рамках транзакции удаляем все записи из таблицы PhoneRange и вставляем новые.
         Таким образом БД полностью синхронизируется с CSV-данными.
    """
    from apps.operator_by_phone.models import PhoneRange

    log.info("Task update_phone_ranges started.")

    HEADERS = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://opendata.digital.gov.ru/'
    }

    # Список для хранения всех записей из всех CSV
    combined_records = []

    # Обрабатываем каждый URL из источника
    for url in settings.REGISTER_OF_NUMBERING:
        log.info(f"Processing URL: {url}")
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
        except Exception as e:
            log.error(f"Request error: {e}")
            continue

        lines = response.content.decode('utf-8', errors='ignore').splitlines()
        reader = csv.reader(lines, delimiter=';')
        header_skipped = False

        for row in reader:
            if not header_skipped:
                header_skipped = True
                continue
            if len(row) < 4:
                continue
            try:
                code = row[0].strip()
                start = int(row[1])
                end = int(row[2])
                capacity = int(row[3]) if row[3].strip() != "" else None
                operator = row[4].strip() if len(row) > 4 else ""
                region = row[5].strip() if len(row) > 5 else ""
                territory = row[6].strip() if len(row) > 6 else ""
                inn = row[7].strip() if len(row) > 7 else ""
                combined_records.append({
                    'code': code,
                    'start': start,
                    'end': end,
                    'capacity': capacity,
                    'operator': operator,
                    'region': region,
                    'territory': territory,
                    'inn': inn,
                })
            except Exception as parse_err:
                log.error(f"Parse error row {row}: {traceback_str(parse_err)}")
                continue

        log.info(f"Done with URL: {url}")

    if not combined_records:
        log.info("No records obtained from CSV.")
        return

    # Группируем записи по уникальному ключу (code, start, end)
    unique_records = {}
    for rec in combined_records:
        key = (rec['code'], rec['start'], rec['end'])
        unique_records[key] = rec  # если дублируется, берется последнее значение

    new_records = list(unique_records.values())
    total_new = len(new_records)
    log.info(f"Total unique records for synchronization: {total_new}")

    # Устанавливаем таймаута для БД
    if connection.vendor == 'sqlite':
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA busy_timeout = 50000")
    elif connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("SET lock_timeout = '50s'")
    try:
        with transaction.atomic():
            PhoneRange.objects.all().delete()
            # Формируем объекты для bulk_create
            new_objs = [
                PhoneRange(
                    code=rec['code'],
                    range_start=rec['start'],
                    range_end=rec['end'],
                    capacity=rec['capacity'],
                    operator=rec['operator'],
                    region=rec['region'],
                    territory=rec['territory'],
                    inn=rec['inn'],
                )
                for rec in new_records
            ]
            PhoneRange.objects.bulk_create(new_objs)
            log.info(f"Synchronization completed: {total_new} records inserted.")
    except Exception as e:
        log.info(f"Sync error: {e}")
    log.info("=== update_phone_ranges completed ===")
