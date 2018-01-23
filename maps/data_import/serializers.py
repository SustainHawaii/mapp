from maps.data_import.models import *
from rest_framework_mongoengine import serializers
from rest_framework import serializers as drf_serializers

class DataImportSimpleSerializer(serializers.MongoEngineModelSerializer):
    group = drf_serializers.Field(source='group') 
    datatype = drf_serializers.Field(source='datatype')

    class Meta:
        model = DataImport
        fields = ('id', 'description', 'name', 'group', 'datatype' )

class DataImportSerializer(serializers.MongoEngineModelSerializer):
    class Meta:
        model = DataImport

    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        super(DataImportSerializer, self).__init__(*args, **kwargs)

        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)

class DataSerializer(serializers.MongoEngineModelSerializer):
    class Meta:
        model = Data
        exclude = ('id', 'import_id')
