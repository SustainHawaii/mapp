import unittest
import mock

from django.core.urlresolvers import resolve

from django.test import RequestFactory
from rest_framework.test import APIRequestFactory

from maps.locations.models import LocationType, Location
from maps.categories.models import Categories


class TestLocationTypesApi(unittest.TestCase):

    def setUp(self):
        self.request = APIRequestFactory()

    def tearDown(self):
        pass

    def test_listview_post_req_with_customform_empty_saves_to_db(self):
        if LocationType.objects.filter(name="shtate"):
            LocationType.objects.get(name="shtate").delete()
        loctype = {"name": "shtate",
                   "allow_media": False,
                   "allow_galleries": False,
                   "allow_forms": False,
                   "allow_categories": False,
                   "created": "2015-07-27T00:00:00",
                   "last_updated": "2015-07-27T00:00:00",
                   "view_privacy": "everyone"}
        request = self.request.post('/api/v1/locationtype/', loctype)
        response = resolve('/api/v1/locationtype/').func(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(LocationType.objects.get(name="shtate"))

class TestLocationsApi(unittest.TestCase):

    def setUp(self):
        self.request = APIRequestFactory()

    def tearDown(self):
        pass

    def test_listview_post_req_with_customform_empty_saves_to_db(self):
        if Location.objects.filter(name="test"):
            Location.objects.get(name="test").delete()
        loc = {"name": "test",
               "address1": "6600 Kalanianaole Hwy",
               "zip": "96825",
               "city": "Honolulu",
               "state": "HI",
               "phone": "039485493"}
        request = self.request.post('/api/v1/location/', loc)
        response = resolve('/api/v1/location/').func(request)
        self.assertEqual(response.status_code, 201)
        dbLoc = Location.objects.get(name="test")
        self.assertTrue(dbLoc)
        dbLoc.delete()

    def test_get_location_with_categories(self):
        if Location.objects.filter(name="test"):
            Location.objects.get(name="test").delete()

        for c in Categories.objects.filter(name="test cat"):
            c.delete()

        loc = Location(name = "test")
        loc.save()

        cat = Categories(name="test cat", tagged=[loc])
        cat.save()
        self.assertEqual(1, cat.number_using)

        #start the test
        request = self.request.get('/api/v1/location/' + str(loc.id))
        view, args, kwargs = resolve('/api/v1/location/'+ str(loc.id)+"/")
        kwargs['request'] = request
        response = view(*args, **kwargs).render()
        tagged= response.data['tags'][0]
        self.assertEqual(1, len(response.data['tags']))
        self.assertEqual("test cat", tagged['name'])

        cat.delete()
        loc.delete()
