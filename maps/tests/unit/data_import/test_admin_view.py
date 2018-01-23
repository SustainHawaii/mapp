import json
import geojson
import unittest
from mock import MagicMock, patch
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory

from maps.data_import.admin_view import (SettingsImportSystemView,
                                         SettingsImportFileView,
                                         parse_json,
                                         flatten_json,
                                         make_normalization_entry,
                                         build_normalization_dict,
                                         should_normalize,
                                         update_categories)
from maps.locations.models import LocationType, Location
from maps.org.models import Organization
from maps.data_import.models import Data, DataImport
from maps.categories.models import Categories
from django.core.urlresolvers import resolve
from io import StringIO
from csv import DictReader
import datetime



class NormalizeTest(unittest.TestCase):

    def setUp(self):
        self.expected_dict = { "f1" : 
                             {"datatype" : "integer",
                              "norm_field" : "sf1"},
                         "f2" :
                             {"datatype" : "text",
                              "norm_field" : ""},
                        }
        self.test_dict = {"f1" : "sf1",
                     "f2" : "",
                     "f1_datatype" : "integer",
                     "f2_datatype" : "text",
                    }


    def test_make_normalization_entry(self):
        retval = make_normalization_entry(("f1", "sf1"), self.test_dict)
        self.assertEqual(self.expected_dict["f1"], retval)

    def test_build_normaliztion_dict(self):
        norm = build_normalization_dict(self.test_dict)
        self.assertEqual(self.expected_dict, norm)

    def test_should_normalize(self):
        true_entry = {"datatype" : "integer",
                       "norm_field" : ""}
        self.assertFalse(should_normalize(self.expected_dict["f2"]))
        self.assertTrue(should_normalize(self.expected_dict["f1"]))
        self.assertTrue(should_normalize(true_entry))
                         

class CreateMappingsTests(unittest.TestCase):


    def setUp(self):
        cls = SettingsImportSystemView()
        self.cm = cls.extract_mappings

        file = u"""a,b,c
                   1,2,3
                   3,2,1
                   4,5,6
                   7,8,9"""
        self.file = StringIO(file)

        self.request = APIRequestFactory()

    def tearDown(self):
        pass

    def test_extract_mappingss_returns_dictionary(self):
        self.assertIn(type(self.cm()), [dict, type(None)])

    def test_cm_accepts_csv_file(self):
        self.cm(self.file)

    def test_cm_accepts_request_objects(self):
        request = self.request.post("/maps-admin/settings-importsystem", self.file)
        self.cm(request=request, file=self.file)

    def test_cm_accepts_a_db_model(self):
        self.cm(model=LocationType)

    def test_cm_returns_none_if_any_argument_ommitted(self):
        request = self.request.post("/maps-admin/settings-importsystem", self.file)
        cm = self.cm(request=None, file=None, model=None)
        self.assertIsNone(cm)
        cm = self.cm(request=request, file=None, model=None)
        self.assertIsNone(cm)
        cm = self.cm(request=request, file=self.file, model=None)
        self.assertIsNone(cm)
        cm = self.cm(request=None, file=self.file, model=LocationType)
        self.assertIsNone(cm)

    def test_cm_returns_mappings_in_request(self):
        request = self.request.post("/maps-admin/settings-importsystem",)
        request.DATA = {'a': 'name', 'b': 'desc', 'c': 'taxonomies'}
        cm = self.cm(request=request, file=self.file, model=LocationType)
        self.assertEqual(cm, {'a': 'name',
                              'b': 'desc',
                              'c': 'taxonomies'})


class MakeObjectsTest(unittest.TestCase):

    def setUp(self):
        cls = SettingsImportSystemView()
        self.mkeobj = cls.make_objects

        file = u"""a,b,c
                   1,2,3"""
        self.file = StringIO(file)

        self.mapping = {'a': 'name',
                        'b': 'desc',
                        'c': 'taxonomies'}

        self.request = APIRequestFactory()

    def tearDown(self):
        pass

    def test_update_categories_clears_existing_categories(self):
       di = DataImport(name="junk", duplicate_content="no", 
                      last_updated=datetime.datetime.now(),upload_format="csv",
                      upload_type="1")
       di.save()
       cat = Categories(name="test cat")
       cat.save()
       cat2 = Categories(name="test cat2", tagged=[di])
       cat2.save()

       cat_list= str(cat.id)

       self.assertEqual(0, len(Categories.objects_with("test cat")))
       self.assertEqual(1, len(Categories.for_object(di)))
       self.assertEqual("test cat2", Categories.for_object(di)[0].name)

       update_categories(di, cat_list)

       self.assertEqual(1, len(Categories.objects_with("test cat")))
       self.assertEqual(0, len(Categories.objects_with("test cat2")))

       self.assertEqual(1, len(Categories.for_object(di)))
       self.assertEqual("test cat", Categories.for_object(di)[0].name)

       di.delete()
       cat.delete()

    

    def test_update_categories_work_with_invalid_category(self):
       di = DataImport(name="junk", duplicate_content="no", 
                      last_updated=datetime.datetime.now(),upload_format="csv",
                      upload_type="1")
       di.save()
       cat = Categories(name="test cat")
       cat.save()

       cat_list= "i'm not a category,56485cb53f3aaaaaaaaaaaaa, %s" % (str(cat.id))

       self.assertEqual(0, len(Categories.objects_with("test cat")))
       self.assertEqual(0, len(Categories.for_object(di)))

       update_categories(di, cat_list)

       self.assertEqual(1, len(Categories.objects_with("test cat")))

       self.assertEqual(1, len(Categories.for_object(di)))
       self.assertEqual("test cat", Categories.for_object(di)[0].name)

       di.delete()
       cat.delete()


    def test_update_categories(self):
       di = DataImport(name="junk", duplicate_content="no", 
                      last_updated=datetime.datetime.now(),upload_format="csv",
                      upload_type="1")
       di.save()
       
       cat = Categories(name="test cat")
       cat.save()
       cat2 = Categories(name="test cat2")
       cat2.save()

       cat_list= "%s,%s" %(str(cat.id), str(cat2.id))

       self.assertEqual(0, len(Categories.objects_with("test cat")))
       self.assertEqual(0, len(Categories.objects_with("test cat2")))
       self.assertEqual(0, len(Categories.for_object(di)))

       update_categories(di, cat_list)

       self.assertEqual(1, len(Categories.objects_with("test cat")))
       self.assertEqual(1, len(Categories.objects_with("test cat2")))

       self.assertEqual(2, len(Categories.for_object(di)))
       self.assertEqual("test cat", Categories.for_object(di)[0].name)
       self.assertEqual("test cat2", Categories.for_object(di)[1].name)

       di.delete()
       cat.delete()
       cat2.delete()



    def test_mkeobj_returns_list_or_none(self):
        mkeobj = self.mkeobj()
        self.assertIn(type(mkeobj), [list, type(None)])

    def test_mkeobj_a_list_of_mongo_document_objects(self):
        reader = DictReader(self.file)
        mkeobj = self.mkeobj(data=reader, mapping=self.mapping, model=LocationType)
        lt = LocationType(name='1', desc='2', taxonomies='3')
        self.assertEqual(mkeobj[0].name, lt.name)


    def test_mkeobj_handles_ref_fields(self):
        file = u"""name,loctype,c
                   test_location,new_loc_type,3"""
        loc_file = StringIO(file)

        loc_mapping = {'name': 'name',
                        'loctype': 'location_type'}
        
        #make a location type
        try:
            test_loc_type = LocationType.objects.get(name="new_loc_type")
        except LocationType.DoesNotExist:
            test_loc_type = LocationType(name="new_loc_type")
            test_loc_type.save()

        try:
            #upload the bugger
            reader = DictReader(loc_file)
            mkeobj = self.mkeobj(data=reader, mapping=loc_mapping, model=Location)
            self.assertEqual(mkeobj[0].location_type.name,test_loc_type.name) 
        finally:
            #cleanup
            test_loc_type.delete()

    def test_mkeobj_handels_boolean_field(self):
        file = u"""a,b,c,d
                   1,2,False,True"""
        test_file = StringIO(file)

        test_mapping = {'a': 'name',
                        'b': 'desc',
                        'c': 'allow_media',
                        'd': 'allow_galleries'}
        reader = DictReader(test_file)
        mkeobj = self.mkeobj(data=reader, mapping=test_mapping, model=LocationType)
        lt = LocationType(name='1', desc='2', allow_media=False,
                          allow_galleries=True)
        self.assertEqual(mkeobj[0].allow_media, lt.allow_media)
        self.assertEqual(mkeobj[0].allow_galleries, lt.allow_galleries)

    def test_mkeobj_handels_date_field(self):
        file = u"""a,b,c,d
                   1,2,Jan 15 2015,True"""
        test_file = StringIO(file)

        test_mapping = {'a': 'name',
                        'b': 'desc',
                        'c': 'created',
                        'd': 'allow_galleries'}
        reader = DictReader(test_file)
        mkeobj = self.mkeobj(data=reader, mapping=test_mapping, model=LocationType)
        lt = LocationType(name='1', desc='2', created=datetime.datetime(2015, 1, 15, 0, 0),
                          allow_galleries=True)
        self.assertEqual(mkeobj[0].created, lt.created)

    def test_mkeobj_handels_organization(self):
        file = u"""a,b,c,d
                   1,2,somewhereville"""
        test_file = StringIO(file)

        test_mapping = {'a': 'name',
                        'b': 'description',
                        'c': 'city',
                       }
        reader = DictReader(test_file)
        mkeobj = self.mkeobj(data=reader, mapping=test_mapping,
                             model=Organization)
        org = Organization(name='1', description='2',city="somewhereville")
        self.assertEqual(mkeobj[0].city, org.city)


class SettingsImportoSystemView_PostTests(unittest.TestCase):

    
    def setUp(self):
        self.request = RequestFactory()
        file = u"""a,b,c
                   1,2,3"""
        self.upload_file = StringIO(file)
        self.mock_json = mock_json

    def tearDown(self):
        import string
        [l.delete() for l in LocationType.objects(name__in=list(string.letters + string.digits))]
        [l.delete() for l in LocationType.objects(name__in=['ALPHONSE', 'PETER'])]

    def test_csv_with_no_file_returns_error(self):
        request = self.request.post('/maps-admin/settings-importsystem',
                                    {'upload_format': 0, 'content_type': 1, 'upload_type': 0})
        request.POST._mutable = True
        response = resolve('/maps-admin/settings-importsystem').func(request)
        self.assertEqual(response.data['errors']['upload_file'], 'Import error. Please check the file.')

    def test_csv_with_file_saves_to_database(self):

        request = self.request.post('/maps-admin/settings-importsystem',
                                    {'upload_format': 0, 'content_type': 1, 'upload_type': 0, 'upload_file': self.upload_file,
                                     'a':'name', 'b':'desc','c':'taxonomies'})
        request.POST._mutable = True
        count = LocationType.objects.count()
        with patch("mongoengine.Document.save") as mock_save:
            response = resolve('/maps-admin/settings-importsystem').func(request)
            self.assertTrue(mock_save.called)

    def test_csv_with_same_unique_field_updates_not_inserts(self):
        return
        file = u"""a,b,c
                   %s,2,3""" % "someduplicate"
        
        file = StringIO(file)
        request = self.request.post('/maps-admin/settings-importsystem',
                                    {'upload_format': 0, 'content_type': 1, 'upload_type': 0, 'upload_file': file,
                                     'a':'name', 'b':'desc','c':'taxonomies'})
        request.POST._mutable = True
        count = LocationType.objects.count()
        with patch("mongoengine.Document.save") as mock_save:
            with patch("maps.data_import.admin_view.LocationType.objects") as mock_loc:
                from mongoengine.queryset import NotUniqueError
                mock_save.side_effect=[NotUniqueError, None]
                response = resolve('/maps-admin/settings-importsystem').func(request)
                self.assertTrue(mock_loc.get.called)
                self.assertEqual(mock_save.call_count, 2)

    def test_livefeed_calls_uploaded_url(self):

        request = self.request.post('/maps-admin/settings-importsystem',
                                    {'upload_format': 1, 'content_type': 1, 'upload_type': 1,
                                     'upload_url':'avalidurltodata'})
        with patch('maps.data_import.admin_view.requests') as mock_request:
            mock_request.json.return_value = self.mock_json
            response = resolve('/maps-admin/settings-importsystem').func(request)
            self.assertTrue(mock_request.get.called)

    def test_livefeed_saves_objects_to_database(self):
        request = self.request.post('/maps-admin/settings-importsystem',
                                    {'upload_format': 1, 'content_type': 1, 'upload_type': 1,
                                     'upload_url':'avalidurltodata',
                                     'first_name': 'name',
                                     "last_business_name" : "",
                                     "balance" : "",
                                     "bank_name" : "",
                                     "last_transaction" : "",
                                     "address" : " ",
                                     "city" : ""
                                    })
        with patch('maps.data_import.admin_view.requests.get') as mock_request:
            with patch('mongoengine.Document.save') as mock_save:
                mock_request.status_code = 200
                mock_request().json.return_value = self.mock_json
                response = resolve('/maps-admin/settings-importsystem').func(request)
                self.assertTrue(mock_request.called)
                self.assertTrue(mock_save.called)

    def test_livefeed_handles_inconsistent_json(self):
        """Incases where one json object out of many has a missing field,
           ensure that object is skipped"""
        request = self.request.post('/maps-admin/settings-importsystem',
                                    {'upload_format': 1, 'content_type': 1, 'upload_type': 1,
                                     'upload_url':'avalidurltodata',
                                     'first_name': 'name',
                                     "last_business_name" : "",
                                     "balance" : "",
                                     "bank_name" : "",
                                     "last_transaction" : "",
                                     "address" : " ",
                                     "city" : ""
                                    })
        with patch('maps.data_import.admin_view.requests.get') as mock_request:
            with patch('mongoengine.Document.save') as mock_save:
                mock_request.status_code = 200
                mjson = [] + self.mock_json
                mjson.append(
                    {
                        # missing 'first_name' field
                        "last_business_name" : "FURTAT",
                        "balance" : "73406.84",
                        "bank_name" : "TORONTO-DOMINION BANK ",
                        "last_transaction" : "1987-10-01T12:00:00",
                        "address" : "29 ANDOVER ST ",
                        "city" : "CARLTON NSW 2218 AUS "
                    }
                )
                mock_request().json.return_value = mjson
                response = resolve('/maps-admin/settings-importsystem').func(request)
                self.assertTrue(mock_request.called)
                self.assertTrue(mock_save.called)


class SettingsImportSystemView_Post_GeoJson(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.request = RequestFactory()
        self.mock_json = json.dumps(mock_geojson).decode('utf-8')
        self.file = StringIO(self.mock_json)
        self.mock_bad_json = json.dumps(poorly_formated_geojson).decode('utf-8')
        self.bad_file = StringIO(self.mock_bad_json)

    def tearDown(self):
        self.file.close()

    def test_empty_post_request(self):
        '''Should return "No Data Error"'''
        request = self.request.post('/maps-admin/settings-importfile',
                                    {'upload_format': 1, 'content_type': 0,
                                     'duplicate_content': 0, 'name': 'geojsonee',
                                     'upload_type': 0, 'upload_file': StringIO(u'')})        
        response = resolve('/maps-admin/settings-importsystem').func(request)
        assert(response.status_code == 200)
        self.assertEqual(response.data['errors']['upload_file'], 'Import error. Please check the file.')    

    def test_valid_geojson(self):
        with patch('maps.data_import.admin_view.SettingsImportSystemView.make_locations') as mock_make:
            request = self.request.post('/maps-admin/settings-importsystem',
                                        {'upload_format': 2, 'content_type': 0,
                                         'duplicate_content': 0, 'name': 'geojsonee',
                                         'upload_type': 0, 'upload_file': self.file})
            response = resolve('/maps-admin/settings-importsystem').func(request)
            self.assertTrue(mock_make.called)

    def test_shapefile_conversion_weirdness_removed(self):
        with patch('maps.data_import.admin_view.SettingsImportSystemView.upload_tmk_data') as mock_tmk:
            self.assertTrue(']]], [[[' in json.dumps(self.mock_bad_json))
            request = self.request.post('/maps-admin/settings-importsystem',
                                        {'upload_format': 2, 'content_type': 0,
                                         'duplicate_content': 0, 'name': 'geojsonee',
                                         'upload_type': 0, 'upload_file': self.file})
            response = resolve('/maps-admin/settings-importsystem').func(request)
            self.assertTrue(mock_tmk.called)
            mock_tmk.mock_calls[0][1][0]['features'][0]['geometry']['coordinates'] == mock_geojson['features'][0]['geometry']['coordinates']            

            
class MakeLocations(unittest.TestCase):

    def setUp(self):
        self.mock_json = mock_geojson
        self.mock_NOTMK_json = mock_NOTMK_geojson        

    def tearDown(self):
        pass

    def test_dict_with_TMK_calls_upload_tmk(self):
        with patch('maps.data_import.admin_view.SettingsImportSystemView.upload_tmk_data') as mock_tmk:
            data = self.mock_json
            view = SettingsImportSystemView()
            view.make_locations(data, {})
            self.assertTrue(mock_tmk.called)

    def test_dict_withoutTMK_extract_mappings(self):
        with patch('maps.data_import.admin_view.SettingsImportSystemView.extract_mappings') as mock_map:
            with patch('maps.data_import.admin_view.SettingsImportSystemView.make_objects') as mock_obj:                        
                data = self.mock_NOTMK_json
                view = SettingsImportSystemView()
                view.make_locations(data, {})
                self.assertTrue(mock_map.called)

    def test_dict_withoutTMK_extract_mappings_with_only_properties(self):
        with patch('maps.data_import.admin_view.SettingsImportSystemView.extract_mappings') as mock_map:
            with patch('maps.data_import.admin_view.SettingsImportSystemView.make_objects') as mock_obj:            
                data = self.mock_NOTMK_json
                view = SettingsImportSystemView()
                view.make_locations(data, {})
                self.assertTrue(mock_map.called)
                self.assertEqual(mock_map.call_args[1].get('json'), data.get('features')[0].get('properties'))

    def test_make_obj_return_updated_with_coords(self):
        with patch('mongoengine.Document.save') as mock_save:        
            with patch('maps.data_import.admin_view.SettingsImportSystemView.make_objects') as mock_obj:
                mock_obj.return_value = [Location(name="test")]
                data = self.mock_NOTMK_json
                view = SettingsImportSystemView()
                rv = view.make_locations(data, {})
                self.assertTrue(mock_obj.called)
                self.assertEqual(rv[0].points,
                                 self.mock_NOTMK_json.get('features')[0].get('geometry').get('coordinates'))


class UploadTMkData(unittest.TestCase):

    def setUp(self):
        location_type, created = LocationType.objects.get_or_create(
            name="TMK",
        )
        if created:
            location_type.save()                
        self.mock_json = mock_geojson

    def tearDown(self):
        pass

    def test_dict_with_TMK_calls_upload_tmk(self):
        with patch('mongoengine.Document.save') as mock_save:
            data = self.mock_json
            view = SettingsImportSystemView()
            view.upload_tmk_data (data)
            self.assertTrue(mock_save.called)


class SettingsImportFileView_Post_Json(unittest.TestCase):

    def setUp(self):
        self.request = RequestFactory()
        self.mock_json = json.dumps(mock_json).decode('utf-8')
        self.file = StringIO(self.mock_json)

    def tearDown(self):
        pass

    def test_empty_post_request(self):
        '''Should return "No Data Error"'''
        request = self.request.post('/maps-admin/settings-importfile',
                                    {'upload_format': 1, 'content_type': 1,
                                     'duplicate_content': 0, 'name': 'jsonee',
                                     'upload_type': 0, 'upload_file': StringIO(u'')})        
        response = resolve('/maps-admin/settings-importsystem').func(request)
        assert(response.status_code == 200)
        self.assertEqual(response.data['errors']['upload_file'], 'Import error. Please check the file.')    

    def test_valid_json(self):
        '''Integration Test'''        
        '''Should return 200'''
        request = self.request.post('/maps-admin/settings-importfile',
                                    {'upload_format': 1, 'content_type': 1,
                                     'duplicate_content': 0, 'name': 'jsonee',
                                     'upload_type': 0, 'upload_file': self.file})
        response = resolve('/maps-admin/settings-importfile').func(request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['errors']['msg'])

    
class TestParseJson(unittest.TestCase):

    def setUp(self):
        self.mock_json = mock_json
        self.bad_json = bad_json

    def tearDown(self):
        pass

    def test_flat_json(self):
        '''Should save twice to the database'''
        model = MagicMock(spec=Data)
        obj = MagicMock(spec=DataImport)
        parse_json(self.mock_json, obj, model, False)
        self.assertEqual(model.call_count, 2)

    def test_inconsistent_data_is_not_saved(self):
        '''Should save once to the db'''
        model = MagicMock(spec=Data)
        obj = MagicMock(spec=DataImport)
        parse_json(self.bad_json, obj, model, False)
        self.assertEqual(model.call_count, 1)

    def test_id_field_appended_with_name(self):
        '''any fields named "ID" should be appended with the field value'''
        mjson = [] + self.mock_json
        [j.update({'id':'id'}) for j in mjson]
        model = MagicMock(spec=Data)
        obj = MagicMock(spec=DataImport)
        parse_json(mjson, obj, model, False)
        self.assertTrue(model.call_args_list[0][1]['_id_'])
        

class TestFlattenJson(unittest.TestCase):

    def setUp(self):
        self.mock_json = mock_json

    def tearDown(self):
        pass

    def test_flattens_nested_json(self):
        mjson = []
        [mjson.append({str(len(mjson)): j}) for j in self.mock_json]
        self.assertEqual(len(mjson[0].keys()), 1)                
        flat = flatten_json(mjson)
        self.assertGreater(len(flat[0].keys()), 1)

    def test_list_of_nested_json(self):
        mjson = []
        [mjson.append({str(len(mjson)): j, 'test':'test'}) for j in self.mock_json]
        self.assertEqual(len(mjson[0].keys()), 2)                
        flat = flatten_json(mjson)
        self.assertEqual(len(flat[0].keys()), 8)

    def test_single_key_dict(self):
        '''Of the format {key: [expectedjson]}'''
        mjson = {'key': self.mock_json}
        self.assertEqual(len(mjson), 1)
        flat = flatten_json(mjson)
        self.assertEqual(len(flat), 2)

mock_json = [{
    "last_business_name" : "LACASSE",
    "balance" : "98428.28",
    "first_name" : "ALPHONSE           ",
    "bank_name" : "CANADIAN IMPERIAL BANK OF COMMERCEMMERCE",
    "last_transaction" : "1986-06-10T12:00:00",
    "address" : " ",
    "city": "Test"
},{
    "last_business_name" : "PAYDLI",
    "balance" : "77273.87",
    "first_name" : "PETER        ",
    "bank_name" : "ROYAL BANK OF CANADA ",
    "last_transaction" : "1995-08-17T12:00:00",
    "address" : "9346 86 AVE NW ",
    "city": "testy"
}]

bad_json = [{
    "last_business_name" : "LACASSE",
    "balance" : "98428.28",
    "first_name" : "ALPHONSE           ",
    "bank_name" : "CANADIAN IMPERIAL BANK OF COMMERCEMMERCE",
    "last_transaction" : "1986-06-10T12:00:00",
    "address" : " ",
    "city" : " "
},{
    "inconsistent_name" : "PAYDLI",
    "balance" : "77273.87",
    "first_name" : "PETER        ",
    "bank_name" : "ROYAL BANK OF CANADA ",
    "last_transaction" : "1995-08-17T12:00:00",
    "address" : "9346 86 AVE NW ",
    "city" : "Edmonton"
}]
        
    
mock_geojson = {
    "type": "FeatureCollection",
    "features": [
        { "type": "Feature", "properties": { "OBJECTID": 1, "TMK": 343008002, "MajorOwner": "Govt. State", "BigstOwner": "Govt. State", "TaxAcres": 85.700000, "LandValue": 468400, "LandExempt": 468400, "BldgValue": 0, "BldgExempt": 0, "PittCode": 500, "Homeowner": "N", "GISAcres": 90.405863 }, "geometry": { "type": "Polygon", "coordinates": [ [ [ 880566.196612066356465, 2217472.079331794753671 ], [ 880560.665154730668291, 2217449.017867631278932 ], [ 880545.301878999220207, 2217426.089743734337389 ], [ 880503.478182797553018, 2217385.494032659102231 ], [ 880494.51724688441027, 2217376.748535054270178 ], [ 880460.940631337929517, 2217349.15983963245526 ], [ 880437.755449187709019, 2217321.182859712280333 ], [ 880412.20967601146549, 2217289.484969525132328 ], [ 880401.282486430834979, 2217259.333981380332261 ], [ 880391.235185890225694, 2217216.393386747688055 ], [ 880393.305471795611084, 2217177.98449075082317 ], [ 880397.276630439097062, 2217136.56883529573679 ], [ 880393.20614700531587, 2217099.852743648923934 ], [ 880382.361930745653808, 2217065.437403582036495 ], [ 880380.599586892640218, 2217062.349264851305634 ], [ 880368.247449684655294, 2217013.856953802984208 ], [ 880366.195025928784162, 2216968.63933038385585 ], [ 880361.518931787111796, 2216959.386459635104984 ], [ 880333.75284357147757, 2216917.262345517519861 ], [ 880321.213905713404529, 2216877.31745508313179 ], [ 880323.831400217488408, 2216813.897036446724087 ], [ 880310.590646389988251, 2216777.593021196313202 ], [ 880304.681971656624228, 2216768.916795023251325 ], [ 880284.170586124993861, 2216730.619227489922196 ], [ 880247.913296438753605, 2216686.487659447826445 ], [ 880226.182499246206135, 2216647.554980608168989 ], [ 880211.038983771693893, 2216614.868926260620356 ], [ 880191.69297930970788, 2216580.95039241341874 ], [ 879859.542315942235291, 2216779.150537089444697 ], [ 879895.61367601051461, 2216837.024883890058845 ], [ 879930.930850621778518, 2216891.380192395299673 ], [ 879932.514057276886888, 2216896.155873346608132 ], [ 879940.19346849003341, 2216919.31560123572126 ], [ 880005.474284208728932, 2217148.432676873169839 ], [ 880065.934515679487959, 2217377.598221079912037 ], [ 880080.420499977888539, 2217443.123878034763038 ], [ 880117.759495268110186, 2217641.507669554557651 ], [ 880141.722984003601596, 2217632.339929162058979 ], [ 880378.616522208089009, 2217542.237752350512892 ], [ 880566.196612066356465, 2217472.079331794753671 ] ] ] } }
    ]
}

mock_NOTMK_geojson = {
    "type": "FeatureCollection",
    "features": [
        { "type": "Feature", "properties": { "OBJECTID": 1, "NOTMK": 343008002, "MajorOwner": "Govt. State", "BigstOwner": "Govt. State", "TaxAcres": 85.700000, "LandValue": 468400, "LandExempt": 468400, "BldgValue": 0, "BldgExempt": 0, "PittCode": 500, "Homeowner": "N", "GISAcres": 90.405863 }, "geometry": { "type": "Polygon", "coordinates": [ [ [ 880566.196612066356465, 2217472.079331794753671 ], [ 880560.665154730668291, 2217449.017867631278932 ], [ 880545.301878999220207, 2217426.089743734337389 ], [ 880503.478182797553018, 2217385.494032659102231 ], [ 880494.51724688441027, 2217376.748535054270178 ], [ 880460.940631337929517, 2217349.15983963245526 ], [ 880437.755449187709019, 2217321.182859712280333 ], [ 880412.20967601146549, 2217289.484969525132328 ], [ 880401.282486430834979, 2217259.333981380332261 ], [ 880391.235185890225694, 2217216.393386747688055 ], [ 880393.305471795611084, 2217177.98449075082317 ], [ 880397.276630439097062, 2217136.56883529573679 ], [ 880393.20614700531587, 2217099.852743648923934 ], [ 880382.361930745653808, 2217065.437403582036495 ], [ 880380.599586892640218, 2217062.349264851305634 ], [ 880368.247449684655294, 2217013.856953802984208 ], [ 880366.195025928784162, 2216968.63933038385585 ], [ 880361.518931787111796, 2216959.386459635104984 ], [ 880333.75284357147757, 2216917.262345517519861 ], [ 880321.213905713404529, 2216877.31745508313179 ], [ 880323.831400217488408, 2216813.897036446724087 ], [ 880310.590646389988251, 2216777.593021196313202 ], [ 880304.681971656624228, 2216768.916795023251325 ], [ 880284.170586124993861, 2216730.619227489922196 ], [ 880247.913296438753605, 2216686.487659447826445 ], [ 880226.182499246206135, 2216647.554980608168989 ], [ 880211.038983771693893, 2216614.868926260620356 ], [ 880191.69297930970788, 2216580.95039241341874 ], [ 879859.542315942235291, 2216779.150537089444697 ], [ 879895.61367601051461, 2216837.024883890058845 ], [ 879930.930850621778518, 2216891.380192395299673 ], [ 879932.514057276886888, 2216896.155873346608132 ], [ 879940.19346849003341, 2216919.31560123572126 ], [ 880005.474284208728932, 2217148.432676873169839 ], [ 880065.934515679487959, 2217377.598221079912037 ], [ 880080.420499977888539, 2217443.123878034763038 ], [ 880117.759495268110186, 2217641.507669554557651 ], [ 880141.722984003601596, 2217632.339929162058979 ], [ 880378.616522208089009, 2217542.237752350512892 ], [ 880566.196612066356465, 2217472.079331794753671 ] ] ] } }
    ]
}

poorly_formated_geojson = {
    "type": "FeatureCollection",
    "features": [
        { "type": "Feature", "properties": { "OBJECTID": 1, "TMK": 343008002, "MajorOwner": "Govt. State", "BigstOwner": "Govt. State", "TaxAcres": 85.700000, "LandValue": 468400, "LandExempt": 468400, "BldgValue": 0, "BldgExempt": 0, "PittCode": 500, "Homeowner": "N", "GISAcres": 90.405863 }, "geometry": { "type": "Polygon", "coordinates": [ [ [ [ 880566.196612066356465, 2217472.079331794753671 ], [ 880560.665154730668291, 2217449.017867631278932 ], [ 880545.301878999220207, 2217426.089743734337389 ], [ 880503.478182797553018, 2217385.494032659102231 ], [ 880494.51724688441027, 2217376.748535054270178 ], [ 880460.940631337929517, 2217349.15983963245526 ], [ 880437.755449187709019, 2217321.182859712280333 ], [ 880412.20967601146549, 2217289.484969525132328 ], [ 880401.282486430834979, 2217259.333981380332261 ], [ 880391.235185890225694, 2217216.393386747688055 ], [ 880393.305471795611084, 2217177.98449075082317 ], [ 880397.276630439097062, 2217136.56883529573679 ], [ 880393.20614700531587, 2217099.852743648923934 ], [ 880382.361930745653808, 2217065.437403582036495 ], [ 880380.599586892640218, 2217062.349264851305634 ], [ 880368.247449684655294, 2217013.856953802984208 ], [ 880366.195025928784162, 2216968.63933038385585 ], [ 880361.518931787111796, 2216959.386459635104984 ], [ 880333.75284357147757, 2216917.262345517519861 ], [ 880321.213905713404529, 2216877.31745508313179 ], [ 880323.831400217488408, 2216813.897036446724087 ], [ 880310.590646389988251, 2216777.593021196313202 ], [ 880304.681971656624228, 2216768.916795023251325 ], [ 880284.170586124993861, 2216730.619227489922196 ], [ 880247.913296438753605, 2216686.487659447826445 ], [ 880226.182499246206135, 2216647.554980608168989 ], [ 880211.038983771693893, 2216614.868926260620356 ], [ 880191.69297930970788, 2216580.95039241341874 ], [ 879859.542315942235291, 2216779.150537089444697 ], [ 879895.61367601051461, 2216837.024883890058845 ], [ 879930.930850621778518, 2216891.380192395299673 ], [ 879932.514057276886888, 2216896.155873346608132 ], [ 879940.19346849003341, 2216919.31560123572126 ], [ 880005.474284208728932, 2217148.432676873169839 ], [ 880065.934515679487959, 2217377.598221079912037 ], [ 880080.420499977888539, 2217443.123878034763038 ], [ 880117.759495268110186, 2217641.507669554557651 ], [ 880141.722984003601596, 2217632.339929162058979 ], [ 880378.616522208089009, 2217542.237752350512892 ]]], [[[ 880566.196612066356465, 2217472.079331794753671 ] ] ] ] } }
    ]
}





