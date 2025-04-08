gunicorn --bind 0.0.0.0:8000 freelance_platform.asgi:application -k uvicorn.workers.UvicornWorker &
celery -A freelance_platform worker -l info