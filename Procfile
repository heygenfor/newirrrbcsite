web: gunicorn bankingsystem.wsgi --log-file -

web: python manage.py migrate && gunicorn bankingsystem.wsgi
