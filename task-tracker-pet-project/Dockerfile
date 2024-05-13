FROM python:3.11-alpine

WORKDIR /app
COPY . /app/

RUN pip install -r requirements.txt

CMD python manage.py migrate \
    && python manage.py loaddata db_dump.json \
    && python manage.py collectstatic --noinput \
    && gunicorn task_tracker.wsgi:application --bind 0.0.0.0:8000
