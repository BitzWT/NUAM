"""
WSGI config for nuamSettings project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv
import pymysql

pymysql.install_as_MySQLdb()
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuamSettings.settings')

application = get_wsgi_application()
