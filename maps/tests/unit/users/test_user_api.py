import unittest
import mock

from django.core.urlresolvers import resolve

from django.test import RequestFactory
from rest_framework.test import APIRequestFactory


# class TestUserTypesApi(unittest.TestCase):

#     def setUp(self):
#         self.request = APIRequestFactory()

#     def tearDown(self):
#         pass

#     def test_listview_post_req_with_customform_empty_saves_to_db(self):
#         usertype = {"id": "", "name": "sometype", "is_superuser": False, "permissions": {"locations": {"2": True, "6": True}, "category": {"2": True, "6": True}, "users": {
#             "2": True, "6": True}, "forms": {"2": True, "6": True}}, "allow_register": True, "need_authorization": True, "custom_field_form": "[]"}
#         request = self.request.post('/api/v1/usertypes/', usertype)
#         response = resolve('/api/v1/usertypes/').func(request)
#         self.assertEqual(response.status_code, 200)
