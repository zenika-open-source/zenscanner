#!/bin/sh

UID_DOCKER=$(ls -l /var/run/docker.sock | cut -d ' ' -f 3)
usermod -u $UID_DOCKER zenscanner
su zenscanner
export PYTHONWARNINGS="ignore"
celery -A core worker -l INFO -Q scanner