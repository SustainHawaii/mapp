from django.test import TestCase, override_settings
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from maps.core import Requester
from maps.core import api
#used to mock out responses
import responses
import requests
import json

# Create your tests here.
class RequesterTests(TestCase):

    @override_settings(CORE_API_URL="http://127.0.0.1:8000/api/v1/")
    def test_get_coreAPIUrl_from_settings(self):
        r = Requester()
        self.assertEquals(r.base_url, "http://127.0.0.1:8000/api/v1/")

    @override_settings(CORE_API_URL="http://127.0.0.1:8000/api/v1/")
    def test_get_coreAPIUrl_from_settings_adds_trailing_slash(self):
        r = Requester()
        self.assertEquals(r.base_url, "http://127.0.0.1:8000/api/v1/")

    def test_get_coreAPIUrl_from_settings_if_setting_not_present(self):
        old = settings._wrapped.__dict__.pop("CORE_API_URL")
        with self.assertRaises(ImproperlyConfigured):
            r = api.Requester()
        settings._wrapped.__dict__["CORE_API_UR"] = old

    @override_settings(CORE_API_URL="http://127.0.0.1:8000/api/v1/")
    @responses.activate
    def test_get_successful(self):

        #setup the mocked respons
        body ='{"test": "data"}'
             
        responses.add(responses.GET, "http://127.0.0.1:8000/api/v1/location/",body=body,
                      status=200, content_type='application/json')

        r = Requester()
        resp = r.get("location")

        self.assertEquals(len(responses.calls), 1)
        self.assertEquals(resp, json.loads(body))

    @override_settings(CORE_API_URL="http://127.0.0.1:8000/api/v1/")
    @responses.activate
    def test_get_by_id(self):

        #setup the mocked respons
        body ='{"test": "data"}'
             
        responses.add(responses.GET, "http://127.0.0.1:8000/api/v1/location/1/",body=body,
                      status=200, content_type='application/json')

        r = Requester()
        resp = r.get("location",1)

        self.assertEquals(len(responses.calls), 1)
        self.assertEquals(resp, json.loads(body))

    @override_settings(CORE_API_URL="http://127.0.0.1:8000/api/v1/")
    @responses.activate
    def test_get_call_failes(self):

        #setup the mocked respons
        body ='{"test": "data"}'
             
        responses.add(responses.GET, "http://127.0.0.1:8000/api/v1/location/",body=body,
                      status=404, content_type='application/json')

        r = Requester()
        with self.assertRaises(requests.HTTPError):
            resp = r.get("location")

        self.assertEquals(len(responses.calls), 1)


@override_settings(CORE_API_URL="http://127.0.0.1:8000/api/v1/")
class LocationAPITests(TestCase):

    @responses.activate
    def test_get_call_failes(self):

        #setup the mocked respons
        body ='{"test": "data"}'
             
        responses.add(responses.GET, "http://127.0.0.1:8000/api/v1/location/",body=body,
                      status=404, content_type='application/json')

        with self.assertRaises(requests.HTTPError):
            r = api.locations.get()

        self.assertEquals(len(responses.calls), 1)

    @override_settings(CORE_API_URL="http://127.0.0.1:8000/api/v1/")
    @responses.activate
    def test_get_by_id(self):

        #setup the mocked respons
        body ='{"test": "data"}'
             
        responses.add(responses.GET,
                      "http://127.0.0.1:8000/api/v1/location/7jdkl38ldjndkl390fklnilso/",body=body,
                      status=200, content_type='application/json')


        resp = api.locations.get(id='7jdkl38ldjndkl390fklnilso')

        self.assertEquals(len(responses.calls), 1)
        self.assertEquals(resp, json.loads(body))

