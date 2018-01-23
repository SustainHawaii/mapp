from rest_framework_mongoengine import serializers
from maps.resources.models import Resources, Settings
from rest_framework.serializers import WritableField
from maps.data_visualization.serializers import DataVisualizationSerializer


class ResourcesSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)
    page_background = serializers.fields.CharField(required=False)
    page_background_url = serializers.fields.CharField(read_only=True)
    page_logo = serializers.fields.CharField(required=False)
    page_logo_url = serializers.fields.CharField(read_only=True)
    #save the main_map data viz, but we will save it manually in the post_save,
    #so make it read only here
    main_map = DataVisualizationSerializer(source="main_map", many=False,
                                          read_only=True)

    class Meta:
        model = Resources
        depth = 3

class SettingsSerializer(serializers.MongoEngineModelSerializer):

    class Meta:
        model = Settings
        depth = 2
