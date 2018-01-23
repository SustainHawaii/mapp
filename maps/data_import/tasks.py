import celery
import datetime
import requests
from admin_view import parse_json
from maps.dataimport.models import DataImport, Data
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
INTERVAL = datetime.timedelta(days=1)


@celery.decorators.periodic_task(run_every=INTERVAL)
def import_live_feed():
    for obj in DataImport.objects.filter(upload_type='1'):
        delta = datetime.datetime.now() - obj.last_updated
        freq = datetime.timedelta(days=obj.upload_freq)
        if delta > freq:
            req = requests.get(obj.upload_url)
            if req.status_code != 200:
                logger.warning('Live feed import failed: ' + obj.upload_url)
            else:
                parse_json(req.json(), obj, Data)
                setattr(obj, 'last_updated', datetime.datetime.now())
                obj.save()
