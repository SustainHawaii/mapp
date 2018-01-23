import unittest
import mock

from django.core.urlresolvers import resolve

from django.test import RequestFactory
from rest_framework.test import APIRequestFactory

from maps.categories.models import Categories


class TestCategoriesApi(unittest.TestCase):

    def setUp(self):
        self.request = APIRequestFactory()

    def tearDown(self):
        pass

    def test_listview_post_req_with_customform_empty_saves_to_db(self):
        if Categories.objects.filter(name="test"):
            Categories.objects.get(name="test").delete()
        category = {"name": "test",
                   "description": "test category",
                   "created": "2015-07-27T00:00:00",
                   "last_updated": "2015-07-27T00:00:00",
                   "privacy": "everyone"}
        request = self.request.post('/api/v1/categories/', category)
        response = resolve('/api/v1/categories/').func(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Categories.objects.get(name="test"))
