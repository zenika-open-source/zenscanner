#!/bin/sh

export PYTHONWARNINGS="ignore"
python manage.py migrate
celery -A core worker -l INFO -Q api &
celery -A core beat -l INFO &
python -W ignore manage.py runserver 0.0.0.0:8080
