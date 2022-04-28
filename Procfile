release: python manage.py migrate
web: gunicorn crypto_tax_checker.wsgi --log-file -
worker: celery -A crypto_tax_checker worker -l INFO
