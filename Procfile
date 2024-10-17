web: gunicorn server.wsgi
release: python manage.py makemigrations
release: python manage.py migrate
release: cd ./frontend && npm install && npm run build