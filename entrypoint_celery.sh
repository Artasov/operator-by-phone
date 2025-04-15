#!/bin/sh
echo "#####################################"
echo "######### Celery Starting... ########"
echo "#####################################"
cd /srv/src || exit
celery -A config worker -l INFO --pool=solo -E