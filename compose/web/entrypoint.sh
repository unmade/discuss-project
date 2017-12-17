#!/usr/bin/env sh
export DJANGO_DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}

cmd="$@"
exec $cmd