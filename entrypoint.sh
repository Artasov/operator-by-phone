set -e

cd /srv/src

echo "Waiting for PostgreSQL to be ready..."
export PGPASSWORD="$DB_PASSWORD"

while ! pg_isready -h "$DB_HOST" -p 5432 -U "$DB_USER" -d "$DB_NAME"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL IS UP - continuing"

echo "-----------------------"
echo "Collecting static files"
echo "-----------------------"
python manage.py collectstatic --noinput

echo "------------"
echo "Migrating..."
echo "------------"
python manage.py migrate

echo "------------"
echo "Create SuperUser if not exists..."
echo "------------"
python manage.py autosucreate

echo "----------------------------------"
echo "Gunicorn Starting..."
echo "----------------------------------"
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
