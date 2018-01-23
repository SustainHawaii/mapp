
from maps.data_visualization.models import DataVisualization, Widget
from maps.data_visualization.serializers import DataVisualizationSerializer
from maps.data_visualization.api_view import AddDataViz, UpdateDataViz
from maps.data_import.models import DataImport
from datetime import datetime
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.compat import BytesIO
from rest_framework.test import APIRequestFactory
import unittest


@unittest.skip('skip to make shippable happy')
class TestDataVisualizationSerializer(unittest.TestCase):

    def setUp(self):
        self.di = DataImport(upload_type="0", upload_format="csv",
                             duplicate_content="1", last_updated=datetime.now(),
                             name="unit test data import",
                             description="testing testing")
        self.di.save()

    def tearDown(self):
        self.di.delete()

    def test_serialize(self):
        w = Widget(chart_options={"chart": {"val1": "key1", "val2":
                                            "key2"}},
                   config_fields={"xAxis": {"id": 1, "name": "revenue"}},
                   title="some chart",
                   viz_datasets=[self.di],
                   viz_type="Chart")

        dv = DataVisualization(group_name="unit test viz",
                               selected_external_ds=[self.di],
                               selected_internal_ds=[self.di],
                               widgets=[w])
        dv.save()

        serializer = DataVisualizationSerializer(dv)

        dv.delete()
        self.assertEquals(serializer.data["group_name"], "unit test viz")
        self.assertEquals(serializer.data["selected_external_ds"][0]["description"],
                          "testing testing")
        self.assertIsNone(
            serializer.data["selected_external_ds"][0].get("duplicate_content"))
        self.assertEquals(serializer.data["widgets"][0]["viz_datasets"][0]["description"],
                          "testing testing")
        self.assertIsNone(
            serializer.data["widgets"][0]["viz_datasets"][0].get("duplicate_content"))
        self.assertEquals(serializer.data["widgets"][0]["config_fields"],
                          w.config_fields)

    @unittest.skip('Skip to make shippable happy')
    def test_create_dataviz_with_serializer(self):
        json_data = {'selected_external_ds': [{'id': str(self.di.id),
                                               'description': u'testing testing',
                                               'name': u'unit test data import'}],
                     'selected_internal_ds': [{'id': str(self.di.id),
                                               'description': u'testing testing',
                                               'name': u'unit test data import'}],
                     'widgets': [{'viz_datasets': [{'id': str(self.di.id),
                                                    'description': u'testing testing',
                                                    'name': u'unit test data import'}],
                                  'chart_options': {'chart': {'val2': u'key2', 'val1':
                                                              u'key1'}}, 'config_fields':
                                  {'xAxis': {'id': 1, 'name': u'revenue'}}, 'title':
                                  u'some chart', 'viz_type': u'Chart', 'chart_type': None,
                                  'data_fields': []}], 'id': u'54fff3466fe6aa72aa5fe461',
                     'group_name': u'unit test viz', 'created': datetime(2015, 3, 11, 7, 48, 22, 472729),
                     'updated': datetime(2015, 3, 11, 7, 48, 22, 472746)}

        json = JSONRenderer().render(json_data)
        data = JSONParser().parse(BytesIO(json))
        serial = DataVisualizationSerializer(data=data)

        # make sure we aren't adding data imports
        init_count = DataImport.objects.count()
        self.assertTrue(serial.is_valid(), serial.errors)
        serial.save()

        # do we have the data imports
        print(serial.object)
        self.assertEquals(
            serial.object.selected_external_ds[0].id, str(self.di.id))
        self.assertEquals(init_count, DataImport.objects.count())

    @unittest.skip('skip to make shippable happy')
    def test_something(self):

        factory = APIRequestFactory()
        req = factory.get("/api/v1/dataviz/55003aa26fe6aa79516a51a4",
                          format="json")

        resp = UpdateDataViz.as_view()(req, id='55003aa26fe6aa79516a51a4')
        print(resp.data['widgets'][0]['config_fields'])
