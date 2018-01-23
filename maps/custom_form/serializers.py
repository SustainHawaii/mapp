from rest_framework_mongoengine import serializers
from maps.custom_form.models import FormSchema, FormData


class FormSchemaSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)

    class Meta:
        model = FormSchema
        depth = 1
        fields = ('field_groups', 'created', 'last_updated')


class FormSchemaIdSerializer(serializers.MongoEngineModelSerializer):

    class Meta:
        model = FormSchema
        depth = 1
        fields = ('id', 'field_groups')


class FormDataSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)

    class Meta:
        model = FormData
        depth = 1
        fields = ('form_schema', 'location', 'user', 'data', 'created', 'last_updated')
