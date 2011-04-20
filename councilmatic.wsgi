import os
import sys

ROOT = os.path.dirname(__file__)
PARENT = os.path.dirname(ROOT)

if PARENT not in sys.path:
    sys.path.append(PARENT)

if ROOT not in sys.path:
    sys.path.append(ROOT)

os.environ['DJANGO_SETTINGS_MODULE'] = 'philly_legislative.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
