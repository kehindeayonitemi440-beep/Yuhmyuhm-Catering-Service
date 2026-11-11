# Yuhm Yuhm Catering Services (Django)

## Run locally
    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py makemigrations catering          # skip if catering/migrations already exists
    python manage.py migrate
    python manage.py seed_menu                        # starter dishes and sample reviews
    python manage.py createsuperuser
    WHATSAPP_NUMBER=2349123323596 
    python manage.py runserver

Site: http://127.0.0.1:8000/   Admin: http://127.0.0.1:8000/admin/
Manage dishes, reviews and booking enquiries in the admin.

## Deploy to Render

1. Push this repository to GitHub and create a new Render Blueprint from it. Render
   will use `render.yaml` to build and start the Django web service.
2. Create a PostgreSQL database in Render and set the service's `DATABASE_URL`
   environment variable to that database's **internal** connection string. The
   Blueprint deliberately leaves this value for you to provide, so you can select
   the database plan that fits your needs. Production settings refuse to start
   without a database URL rather than storing business data in ephemeral SQLite.
3. Set `WHATSAPP_NUMBER` in the Render service environment if you want to change
   the default contact number. Render's external hostname is added to Django's
   allowed hosts and CSRF trusted origins automatically. If you add a custom
   domain, add it to `DJANGO_ALLOWED_HOSTS` and add its `https://` origin to
   `DJANGO_CSRF_ORIGINS`.

The service installs dependencies and collects static files during the build;
that build step uses a temporary SQLite URL only for static collection. The
running service requires the configured PostgreSQL URL. Database migrations run
on startup. To create an admin account after the first deploy, use Render's shell
for the service and run
`python manage.py createsuperuser`.
# Yuhmyuhm-Catering-Service
# Yuhmyuhm-Catering-Service
# Yuhmyuhm
