#!/bin/sh
echo "#####################################"
echo "######### Beat Starting... ##########"
echo "#####################################"
cd /srv/src || exit
# Если предпочитаете запускать Beat через Django-менеджер, запускаем через manage.py
python manage.py startbeat