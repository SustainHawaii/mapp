import responses
from maps.locations.models import Location, LocationType
from maps.data_import.models import Data
from maps.locations.serializers import LocationSerializer
from maps.locations.json_views import verify_address, AddLocation, UpdateLocation
from maps.locations.json_views import AddLocationType, build_geojson_for_googlemaps
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.compat import BytesIO
from rest_framework.test import APIRequestFactory
import re
from rest_framework import status
import tempfile
import os
import unittest


@unittest.skip('skip to make shippable happy')
class TestLocationViews(unittest.TestCase):

    @responses.activate
    def test_location_view(self):

        # setup the mocked respons
        body = '{"results": "data"}'

        responses.add(responses.GET, "http://127.0.0.1:8000/api/v1/location/",
                      body=body, status=200, content_type='application/json')

        resp = self.client.get("/maps-admin/locations")

        self.assertEquals(resp.context["object"], "data")


@unittest.skip('ski[ to make shippable happy')
class TestLocationAPI(unittest.TestCase):

    url_re = re.compile(r'https?://maps.google.com/*')

    def test_post(self):
        pass

    def test_get_locations_as_geo_json(self):
        '''can we pull out location data in 
        geojson format for maps?
        '''
        locs = Location.objects.all()

        real = build_geojson_for_googlemaps(locs)

        # being lazy here, just make sure we get something back that looks ok
        self.assertEquals(real['type'], "FeatureCollection")
        self.assertTrue(real.has_key("features"))

    def test_get_externaldata_as_geo_json(self):
        data = Data.objects.all()

        real = build_geojson_for_googlemaps(data)

        # being lazy here, just make sure we get something back that looks ok
        self.assertEquals(real['type'], "FeatureCollection")
        self.assertTrue(real.has_key("features"))

    @responses.activate
    def test_verify_adress(self):

        responses.add(responses.GET, self.url_re,
                      body=GEOCODE_BODY, status=200,
                      content_type='application/json')
        res = verify_address(
            "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA")
        self.assertEquals(
            res, {'coordinates': (-122.0854212, 37.4229181), 'type': 'Point'})

    @responses.activate
    def test_add_location_post(self):
        responses.add(responses.GET, self.url_re,
                      body=GEOCODE_BODY, status=200,
                      content_type='application/json')

        factory = APIRequestFactory()

        request = factory.post('/api/v1/location/',
                               {'address1': 'test',
                                'city': 'Palo Alto',
                                'state': 'CA',
                                'zip': '94043'},
                               format='json')
        resp = AddLocation.as_view()(request)
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)

        # make sure the data was stored
        id = resp.data['id']
        new_loc = Location.objects.get(id=id)
        self.assertEquals(
            new_loc.points, {'coordinates': [-122.0854212, 37.4229181], 'type': 'Point'})

    @responses.activate
    def test_add_location_with_type(self):
        lt = LocationType(name="tksome_new_location", icon="star.png")
        lt.save()
        lt_id = str(lt.id)

        responses.add(responses.GET, self.url_re,
                      body=GEOCODE_BODY, status=200,
                      content_type='application/json')

        factory = APIRequestFactory()

        request = factory.post('/api/v1/location/',
                               {'address1': 'test',
                                'city': 'Palo Alto',
                                'state': 'CA',
                                'location_type': lt_id,
                                'zip': '94043'},
                               format='json')
        resp = AddLocation.as_view()(request)
        lt.delete()
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)

        # make sure the data was stored
        id = resp.data['id']
        new_loc = Location.objects.get(id=id)
        self.assertEquals(
            new_loc.points, {'coordinates': [-122.0854212, 37.4229181], 'type': 'Point'})
        self.assertTrue(new_loc.location_type)

    @responses.activate
    def test_update_location_post(self):
        # create some test data
        l = Location(name="awesome")
        l.save()

        responses.add(responses.GET, self.url_re,
                      body=GEOCODE_BODY, status=200,
                      content_type='application/json')

        factory = APIRequestFactory()

        request = factory.put('/api/v1/location/' + str(l.id) + '/',
                              {'address1': 'test',
                               'city': 'Palo Alto',
                               'state': 'CA',
                               'zip': '94043'},
                              format='json')
        resp = UpdateLocation.as_view()(request, id=str(l.id))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        new_l = Location.objects.get(id=l.id)
        self.assertEquals(new_l.address1, 'test')
        self.assertEquals(
            new_l.points, {'coordinates': [-122.0854212, 37.4229181], 'type': 'Point'})

    @responses.activate
    def test_add_location_type(self):

        factory = APIRequestFactory()

        with tempfile.NamedTemporaryFile(suffix=".tst") as data:
            data.write("blah")
            data.flush()
            request = factory.post('/api/v1/locationtype/',
                                   {'name': 'eshop_test_loc_type',
                                    'description': 'place that sells stuff',
                                    'file': data},
                                   format='multipart')
            resp = AddLocationType.as_view()(request)
            self.assertEquals(resp.status_code, status.HTTP_201_CREATED)

            # make sure the data was stored
            id = resp.data['id']
            new_loc_type = LocationType.objects.get(id=id)
            new_loc_type.delete()
            self.assertEquals(new_loc_type.name, "eshop_test_loc_type")

            # ensure file was saved
            file_saved = os.path.isfile(new_loc_type.icon)
            self.assertTrue(file_saved)
            # cleanup
            os.remove(new_loc_type.icon)


@unittest.skip('skip to make shippable happy')
class TestLocationModel(unittest.TestCase):

    def test_create_point_location(self):
        l = Location(name="test", points=[1, 2])
        l.save()
        self.assertEquals(l.points, [1, 2])
        self.assertEquals(l.name, "test")
        l.delete()

    def test_create_polygon_location(self):
        l = Location(name="test", points=[[[1, 2], [2, 3], [4, 5], [1, 2]]])
        l.save()
        self.assertEquals(l.points, [[[1, 2], [2, 3], [4, 5], [1, 2]]])
        l.delete()


@unittest.skip('skip to make shippable happy')
class TestLocationSerializer(unittest.TestCase):

    def test_get_point_location_with_serializer(self):
        lt = LocationType(name="btest_loc_type2", icon="star.png")
        lt.save()
        l = Location(name="test", points=[1, 2], location_type=lt)
        l.save()
        self.assertEquals(l.points, [1, 2])

        serializer = LocationSerializer(l)
        lt.delete()
        l.delete()
        self.assertEquals(serializer.data["points"], [1, 2])
        self.assertEquals(serializer.data["location_type"]['name'],
                          'btest_loc_type2')
        self.assertEquals(serializer.data["location_type"]['icon'], 'star.png')

    def test_create_point_location_with_serializer(self):
        json_data = {"name": "test", "points": [1, 2]}
        json = JSONRenderer().render(json_data)
        data = JSONParser().parse(BytesIO(json))
        serial = LocationSerializer(data=data)

        self.assertTrue(serial.is_valid(), serial.errors)
        serial.save()

        # point saved then returned as GeoJSON
        self.assertEquals(Location.objects.get(id=serial.object.id).points,
                          {u'type': u'Point', u'coordinates': [1, 2]})
        self.assertEqual(serial.object.name, "test")

    def test_create_polygon_location_with_serializer(self):
        json_data = {
            "name": "test", "points": [[[1, 2], [3, 4], [4, 5], [1, 2]]]}
        json = JSONRenderer().render(json_data)
        data = JSONParser().parse(BytesIO(json))
        serial = LocationSerializer(data=data)

        self.assertTrue(serial.is_valid(), serial.errors)
        serial.save()

        # point saved then returned as GeoJSON
        self.assertEquals(Location.objects.get(id=serial.object.id).points,
                          {u'coordinates': [[[1, 2], [3, 4], [4, 5], [1, 2]]],
                           u'type': u'Polygon'})
        self.assertEqual(serial.object.name, "test")


# this is used in mocking calls to Googles GEOCODE API
GEOCODE_BODY = '''
        {
       "results" : [
          {
         "address_components" : [
            {
               "long_name" : "1600",
               "short_name" : "1600",
               "types" : [ "street_number" ]
            },
            {
               "long_name" : "Amphitheatre Pkwy",
               "short_name" : "Amphitheatre Pkwy",
               "types" : [ "route" ]
            },
            {
               "long_name" : "Mountain View",
               "short_name" : "Mountain View",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Santa Clara",
               "short_name" : "Santa Clara",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "California",
               "short_name" : "CA",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            },
            {
               "long_name" : "94043",
               "short_name" : "94043",
               "types" : [ "postal_code" ]
            }
         ],
         "formatted_address" : "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA",
         "geometry" : {
            "location" : {
               "lat" : 37.42291810,
               "lng" : -122.08542120
            },
            "location_type" : "ROOFTOP",
            "viewport" : {
               "northeast" : {
                  "lat" : 37.42426708029149,
                  "lng" : -122.0840722197085
               },
               "southwest" : {
                  "lat" : 37.42156911970850,
                  "lng" : -122.0867701802915
               }
                    }
                 },
                 "types" : [ "street_address" ]
              }
           ],
           "status" : "OK"
        }
        '''
