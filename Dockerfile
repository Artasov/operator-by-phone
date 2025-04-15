# Базовый образ Python 3.12 на Alpine
FROM python:3.12-alpine AS base

# Скопируем всё в /srv
COPY . /srv
WORKDIR /srv

# Настройки Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установим необходимые пакеты
RUN apk update && \
    apk add --no-cache \
      wget \
      dos2unix \
      libpq-dev \
      netcat-openbsd \
      chrony \
      postgresql-client \
      gcc \
      python3-dev \
      musl-dev \
      linux-headers && \
    python -m pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    cd /srv/src && \
    poetry install --no-root && \
    # Прогоним dos2unix и сделаем скрипты исполняемыми
    dos2unix /srv/entrypoint.sh && chmod +x /srv/entrypoint.sh && \
    dos2unix /srv/entrypoint_celery.sh && chmod +x /srv/entrypoint_celery.sh && \
    dos2unix /srv/entrypoint_beat.sh && chmod +x /srv/entrypoint_beat.sh && \
    # Создадим необходимые папки и дадим права
    mkdir -p /srv/data/cache/ /srv/data/temp/ /srv/src/logs/ /srv/static/ /srv/media/ && \
    chmod -R 777 /srv/data/cache/ /srv/data/temp/ /srv/src/logs/ /srv/static/ /srv/media/ && \
    # Добавим ntp-сервер в конфиг chrony (если нужно синхронизировать время)
    echo "server pool.ntp.org iburst" >> /etc/chrony/chrony.conf

#############
# PROJECT   #
#############
FROM base AS web
ENTRYPOINT ["sh", "/srv/entrypoint.sh"]

#############
# CELERY    #
#############
FROM base AS celery
ENTRYPOINT ["sh", "/srv/entrypoint_celery.sh"]

#############
# BEAT      #
#############
FROM base AS beat
ENTRYPOINT ["sh", "/srv/entrypoint_beat.sh"]
