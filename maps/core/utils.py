import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class Requester(object):

    '''This class is to wrap calls to the sustainhawai/core api server
    it will hide the fact that we are calling a REST API from the end user
    '''

    def __init__(self, endpoint=None):
        self.endpoint = endpoint
        try:
            self.base_url = settings.CORE_API_URL
            if not self.base_url.endswith("/"):
                self.base_url += "/"
        except AttributeError:
            raise(ImproperlyConfigured("Core API requires you set the variable 'CORE_API_URL' in"
                                       "your settings.py file to the base url for the rest API in"
                                       "core_api.  For example 'http://127.0.0.1:8000/api/v1'"
                                       ))

    def get(self, endpoint=None, id=""):
        if self.endpoint:
            endpoint = self.endpoint

        if not endpoint.endswith("/"):
            endpoint += "/"

        if id:
            end = str(id) + "/"
        else:
            end = ""

        res = requests.get(self.base_url + endpoint + end)

        res.raise_for_status()

        return res.json()

