#!/usr/bin/env bash

set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input

python manage.py migrate
python manage.py create_admin
python manage.py google_site_setup