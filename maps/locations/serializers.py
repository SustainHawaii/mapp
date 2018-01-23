from maps.locations.models import LocationType, Location
from rest_framework_mongoengine import serializers
from rest_framework.serializers import Field, WritableField
from maps.categories.serializers import CategoriesSimpleSerializer


class LocationTypeSimpleSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)
    group = Field(source="group")
    # just make is serialize like everybody else
    description = Field(source="long_description")

    class Meta:
        model = LocationType
        fields = ('id', 'name', 'group', 'description', 'last_updated', 'icon')


class LocationTypeSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)
    location_count = Field(source="location_count")

    class Meta:
        model = LocationType
        fields = ('id', 'name', 'allow_media', 'allow_galleries',
                  'allow_forms', 'allow_categories', 'created', 'last_updated',
                  'view_privacy', 'taxonomies', 'icon', 'location_count', 'desc',
                  'custom_field_form')


class LocationSimpleSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)
    group = Field(source="group")

    class Meta:
        model = Location
        fields = ('id', 'name', 'group')


class LocationSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)
    points = WritableField(source="points", required=False)
    image = WritableField(source="image_url", required=False)
    tags = CategoriesSimpleSerializer(source="tags", read_only=True)
    backend_form = serializers.fields.CharField(
        source="backend_form", required=False)
    # taxonomy_custom_form = serializers.fields.CharField(
    #     source="taxonomy_custom_form", required=False)
    taxonomies = serializers.fields.CharField(
        source="taxonomies", required=False)

    class Meta:
        model = Location
        exclude = ('point', 'polygon')

        def save(self):
            print self.validated_data
