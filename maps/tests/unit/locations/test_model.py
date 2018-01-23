import unittest
from mock import Mock, patch
import mock
import json

from maps.locations.models import Location, LocationType
from maps.categories.models import Categories

class MappLocationModel(unittest.TestCase):

    def setUp(self):
        from maps.fixtures.management.commands.create_fixtures import load_data
        load_data()
        self.create_locationtype()
   

    def tearDown(self):
        self.location_type.delete()

    def create_locationtype(self):
        self.location_type = LocationType(name="test_loctype", view_privacy="everyone")
        self.location_type.save()
        self.assertEqual(self.location_type,
                         LocationType.objects.get(name='test_loctype'))

    def test_creating_location(self):
        try:
            loc = Location.objects.get(name='test')
            loc.delete()
        except:
            pass

            
        location = Location(name="test", address1="6600 Kalanianaole Hwy",zip="96825",city="Honolulu",
                                    state="HI",phone="039485493",location_type=self.location_type)
        location.save()
        self.assertEqual(location,
                         Location.objects.get(name='test'))
        location.delete()

    def test_location_get_tags(self):
        for l in Location.objects.filter(name="loc-with-cat2"):
            l.delete()

        loc = Location(name="loc-with-cat2")
        loc.save()
        cat = Categories(name="food-test2", tagged=[loc])
        cat.save()
    
        self.assertIn(cat, loc.tags)
        self.assertEqual(1, len(loc.tags))


        loc.delete()
        cat.delete()
        
        pass


