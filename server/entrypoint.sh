#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
      echo "Waiting for postgres..."

      while ! nc -z $DB_HOST $DB_PORT; do
          sleep 0.1
      done

      echo "PostrgeSQL started"
fi

python manage.py migrate

exec "$@"
