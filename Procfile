web: gunicorn cleaning_service.wsgi --log-file -
worker: celery --app cleaning_service.celery.app worker --loglevel INFO