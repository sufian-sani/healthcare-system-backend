import os
from celery_app import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')  # Change `project` to your project name

app = Celery('project')

# Load settings from Django settings with `CELERY_` namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in installed apps
app.autodiscover_tasks()
