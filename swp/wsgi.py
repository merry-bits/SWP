# -*- coding: utf-8 -*-
from os import environ

from django.core.wsgi import get_wsgi_application


environ.setdefault("DJANGO_SETTINGS_MODULE", "swp.settings.prod")

application = get_wsgi_application()
