import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yuhm_yuhm.settings")
application = get_wsgi_application()
