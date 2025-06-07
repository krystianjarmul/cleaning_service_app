web: gunicorn config.wsgi --log-file -
worker: celery --app config.celery.app worker --loglevel INFO