import unittest
import mock

from django.core.urlresolvers import resolve

from django.test import RequestFactory
from rest_framework.test import APIRequestFactory

from maps.categories.models import Taxonomy


class TestTagsApi(unittest.TestCase):

    def setUp(self):
        self.request = APIRequestFactory()

    def tearDown(self):
        pass

    def test_listview_post_req_with_customform_empty_saves_to_db(self):
        if Taxonomy.objects.filter(name="test"):
            Taxonomy.objects.get(name="test").delete()
        taxonomy = {"name": "test",
                   "description": "test taxonomy",
                   "created": "2015-07-27T00:00:00",
                   "last_updated": "2015-07-27T00:00:00",
                   "privacy": "everyone"}
        request = self.request.post('/api/v1/taxonomy/', taxonomy)
        response = resolve('/api/v1/taxonomy/').func(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Taxonomy.objects.get(name="test"))
