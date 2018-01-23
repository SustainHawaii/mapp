from rest_framework_mongoengine import serializers
from maps.users.models import *


class UserProfileSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)
    email = serializers.fields.CharField(read_only=True)
    confirm_password = serializers.fields.CharField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'email', 'image', 'custom_field_form',
                  'address', 'zip', 'state', 'city', 'description')

    def validate_confirm_password(self, attrs, source):
        value = attrs[source]
        if value != attrs['password']:
            raise serializers.ValidationError('Repeat password is not match.')
        return attrs

    def validate_email(self, attrs, source):
        value = attrs[source]
        query = User.objects.filter(email=value)
        if 'id' in attrs and attrs['id'] != '':
            query = query.filter(id__ne=attrs['id'])

        if len(query) > 0:
            raise serializers.ValidationError('Email already exists.')
        return attrs


class UserTypeSimpleSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)
    group = serializers.fields.CharField(read_only=True, source='group')
    description = serializers.fields.CharField(read_only=True, source="desc")

    class Meta:
        model = UserTypes
        fields = ('id', 'name', 'group', 'description')


class UserTypeSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)

    class Meta:
        model = UserTypes


class UserFormDataSerializer(serializers.MongoEngineModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'image', 'user_types', 'custom_field_form', 'activation_key', 'key_expires')


class UserSerializer(serializers.MongoEngineModelSerializer):
    id = serializers.fields.CharField(read_only=True)
    confirm_password = serializers.fields.CharField(required=True)
    user_types = UserTypeSerializer(source='user_types', many=True)
    primary_user_type = UserTypeSerializer(source='primary_user_type')

    class Meta:
        model = User
        fields = ('id', 'full_name', 'email', 'image', 'user_types', 'organization', 'point',
                  'custom_field_form', 'address', 'zip', 'state', 'city',
                  'description', 'dashboard_resource_id', 'is_active', 'primary_user_type')

    def validate_confirm_password(self, attrs, source):
        value = attrs[source]
        if value != attrs['password']:
            raise serializers.ValidationError('Repeat password is not match.')
        return attrs

    def validate_email(self, attrs, source):
        value = attrs[source]
        query = User.objects.filter(email=value)
        if 'id' in attrs and attrs['id'] != '':
            query = query.filter(id__ne=attrs['id'])
        if len(query) > 0:
            raise serializers.ValidationError('Email already exists.')
        return attrs