#!/bin/sh
echo "#####################################"
echo "######### Beat Starting... ##########"
echo "#####################################"
cd /srv/src || exit
python manage.py startbeat
#celery -A config beat -l INFO