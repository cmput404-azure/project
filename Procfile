# web: cd backend && gunicorn server.wsgi --log-file -
web: cd backend && gunicorn server.wsgi --workers 3 --preload --timeout 30 --access-logfile - --error-logfile - 

#release: python manage.py makemigrations
#release: python manage.py migrate
#release: cd ./frontend && npm install && npm run build
