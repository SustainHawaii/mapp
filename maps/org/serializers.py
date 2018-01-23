from rest_framework_mongoengine import serializers
from .models import Organization


class OrganizationSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)

    class Meta:
        model = Organization