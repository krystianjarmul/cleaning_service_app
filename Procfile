web: gunicorn cleaning_service.wsgi --log-file -
worker: celery -A cleaning_service worker --loglevel=info