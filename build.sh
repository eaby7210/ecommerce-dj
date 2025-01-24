#!/bin/sh

set -o errexit

python manage.py collectstatic --no-input
python manage.py migrate
gunicorn --bind 0.0.0.0:8000 ecommerce.wsgi:application
