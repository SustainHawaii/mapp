from rest_framework_mongoengine import serializers
from .models import Categories, Taxonomy
from rest_framework import serializers as drf_serializers

class CategoriesSimpleSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)
    group = drf_serializers.Field(source='group') 

    class Meta:
        model = Categories
        fields = ('id', 'name','group', 'description')


class CategoriesSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)
    taxonomies = serializers.DynamicField

    class Meta:
        depth = 2
        model = Categories
        exclude = ('tagged',)


class TaxonomySimpleSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)
    group = drf_serializers.Field(source='group') 

    class Meta:
        model = Taxonomy 
        fields = ('id', 'name','group', 'description')

class TaxonomySerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)

    class Meta:
        depth = 5
        model = Taxonomy
