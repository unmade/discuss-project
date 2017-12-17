#!/usr/bin/env sh
cd discuss
python3 manage.py migrate --noinput
/usr/bin/gunicorn discuss.wsgi:application -w 2 -b :8000 --reload
