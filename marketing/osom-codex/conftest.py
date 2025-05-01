import os
import sys
import django
from django.conf import settings

sys.path.append(os.path.join(os.path.dirname(__file__), "dev"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
