#!/bin/sh
set -e

echo "#####################################"
echo "######### Celery Starting... ########"
echo "#####################################"

cd /srv/src || exit

# (При необходимости дождёмся Postgres/Redis, если нужно)
# while ! pg_isready -h "$DB_HOST" -p 5432 -U "$DB_USER" -d "$DB_NAME"; do
#   echo "PostgreSQL is unavailable - sleeping"
#   sleep 2
# done

celery -A config worker -l INFO --pool=solo -E
