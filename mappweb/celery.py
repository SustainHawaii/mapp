from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

#tell celery where to find django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mappweb.settings')

#create the celery app
app = Celery('mappweb')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

#dummy task for testing
@app.task(bind=True)
def debug_task(self):
    print ('Request: {0!r}'.format(self.request))

