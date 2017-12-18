#!/usr/bin/env sh
find . -name "*.pyc" -exec rm -f {} \;

export DJANGO_DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}

cmd="$@"
exec $cmd