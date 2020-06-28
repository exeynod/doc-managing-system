release: python manage.py migrate
release: echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@myproject.com', 'admin')" | python manage.py shell
web: gunicorn SuperKrutoyDocumentooborot.wsgi:application —log-file -