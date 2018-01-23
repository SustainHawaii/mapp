from rest_framework_mongoengine import serializers
from maps.data_visualization.models import DataVisualization, Widget
from maps.data_import.serializers import DataImportSimpleSerializer


class WidgetSerializer(serializers.MongoEngineModelSerializer):
    # viz_datasets = DataImportSimpleSerializer(source="viz_datasets", many=True,
    #                                         allow_add_remove=True)

    class Meta:
        model = Widget


class DataVisualizationSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)
    widgets = WidgetSerializer(
        source="widgets", many=True, allow_add_remove=True)

    class Meta:
        model = DataVisualization
        exclude = ('created', 'updated')
