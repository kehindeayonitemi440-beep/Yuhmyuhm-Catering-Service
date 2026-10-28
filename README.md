# Yuhm Yuhm Catering Services (Django)

## Run locally
    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py makemigrations catering          # skip if catering/migrations already exists
    python manage.py migrate
    python manage.py seed_menu                        # starter dishes and sample reviews
    python manage.py createsuperuser
    WHATSAPP_NUMBER=2348012345678 python manage.py runserver

Site: http://127.0.0.1:8000/   Admin: http://127.0.0.1:8000/admin/
Manage dishes, reviews and booking enquiries in the admin.

## Production
Set DJANGO_SECRET_KEY, DJANGO_DEBUG=0, DJANGO_ALLOWED_HOSTS, DJANGO_CSRF_ORIGINS (https://yourdomain.com)
and WHATSAPP_NUMBER. Run `python manage.py collectstatic --noinput`, then serve with
`gunicorn yuhm_yuhm.wsgi`.
# Yuhmyuhm-Catering-Service
