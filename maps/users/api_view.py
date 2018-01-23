import json

from mongoengine import DoesNotExist
from rest_framework_mongoengine import serializers
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from maps.custom_form.serializers import FormSchemaSerializer
from serializers import *
from maps.users.tasks import send_email_confirmation
from maps.users.serializers import UserFormDataSerializer
from rest_framework_mongoengine import generics as mongo
from rest_framework.response import Response
from rest_framework import status
from maps.users.models import User
from maps.custom_form.models import FormSchema
from utils import save_image
from maps.custom_form.serializers import FormDataSerializer
from maps.custom_form.models import FormData
from maps.users.models import User

site = []


class AddUser(mongo.ListCreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()


    def get_queryset(self):
        filters = self.request.QUERY_PARAMS.get('filter', None)
        if filters:
            return User.objects.filter(name__icontains=filters)[:10]

        return User.objects.all()
    # @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        return super(AddUser, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        site.append(str(request.META['HTTP_HOST']))
        if 'organization' in request.DATA and request.DATA['organization'] is None:
            del request.DATA['organization']

        if 'custom_field_form' in request.DATA:
            self.custom_field_form = json.loads(request.DATA['custom_field_form'])
            del request.DATA['custom_field_form']

        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        try:
            if serializer.is_valid():
                self.pre_save(serializer.object)
                self.object = serializer.save(force_insert=True)
                self.post_save(self.object, created=True)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)
        except serializers.ValidationError:
            return Response({"This Email Already Exists"}, status=status.HTTP_400_BAD_REQUEST)


    def post_save(self, obj, created=False):
        # MongoEngine ReferenceField cannot accept None Type. So have to
        # do the trick here to remove the 'organization'.
        if 'organization' not in self.request.DATA:
            del obj.organization
            obj.save()

        if self.custom_field_form:
            serializer = FormSchemaSerializer(data={'field_groups': self.custom_field_form})
            if serializer.is_valid():
                form_object = serializer.save(force_insert=True)
                obj.custom_field_form = form_object
                obj.save()

        if created:
            obj.set_password(self.request.DATA['password'])
            obj.save()

            send_email_confirmation(site, obj.id)
            f = self.request.FILES.get('file', None)
            save_image(f, obj, 'image', 'full_name', 'user/')


class UpdateUser(mongo.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    custom_field_form = None

    # @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        return super(UpdateUser, self).get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if 'organization' in request.DATA and request.DATA['organization'] is None:
            del request.DATA['organization']
        obj = self.get_object()
        if obj.custom_field_form:
            delattr(obj, 'custom_field_form')
            obj.save()
        if 'custom_field_form' in request.DATA:
            self.custom_field_form = json.loads(request.DATA['custom_field_form'])
            del request.DATA['custom_field_form']

        #if we didn't set password pop it off
        if 'password' in self.request.DATA and self.request.DATA['password'] == "":
            self.request.DATA.pop('password')

        return super(UpdateUser, self).put(request, *args, **kwargs)

    def post_save(self, obj, created=False):
        # MongoEngine ReferenceField cannot accept None Type. So have to
        # do the trick here to remove the 'organization'.
        if 'organization' not in self.request.DATA:
            del obj.organization
            obj.save()

        f = self.request.FILES.get('file', None)
        save_image(f, obj, 'image', 'full_name', 'user/')

        if self.custom_field_form:
            serializer = FormSchemaSerializer(data={'field_groups': self.custom_field_form})
            if serializer.is_valid():
                form_object = serializer.save(force_insert=True)
                obj.custom_field_form = form_object
                obj.save()

        if 'password' in self.request.DATA and self.request.DATA['password'] != '':
            obj.set_password(self.request.DATA['password'])
            obj.save()


class UpdateUserProfile(mongo.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    custom_field_form = None
    primary_user_type = None

    # @method_decorator(login_required(login_url='/'))
    def get(self, request, *args, **kwargs):
        return super(UpdateUserProfile, self).get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        try:
            self.serializer_class = UserProfileSerializer
            # convert json string custom_field_form to object type
            obj = self.get_object()
            if obj.custom_field_form:
                delattr(obj, 'custom_field_form')
                obj.save()

            if 'custom_field_form' in request.DATA:
                self.custom_field_form = json.loads(request.DATA['custom_field_form'])
                del request.DATA['custom_field_form']

            if 'primary_user_type' in request.DATA:
                self.primary_user_type = json.loads(request.DATA['primary_user_type'])

        except Exception as e:
            print e

        return super(UpdateUserProfile, self).put(request, *args, **kwargs)

    def post_save(self, obj, created=False):
        f = self.request.FILES.get('file', None)
        save_image(f, obj, 'image', 'full_name', 'user/')
        if 'password' in self.request.DATA and self.request.DATA['password'] != '':
            obj.set_password(self.request.DATA['password'])
            obj.save()

        # i dont know, how to make serializers to save nested entities in mongoengine, so do it manually
        if self.custom_field_form:
            serializer = FormSchemaSerializer(data={'field_groups': self.custom_field_form})
            if serializer.is_valid():
                form_object = serializer.save(force_insert=True)
                obj.custom_field_form = form_object

        if self.primary_user_type:
            obj.primary_user_type = self._get_primary_type()

        obj.save()

    def _get_primary_type(self):
        """
        Load primary type from db or create new type
        :return: primary type for user
        """
        try:
            return UserTypes.objects.get(id=self.primary_user_type['id'])
        except DoesNotExist:
            serializer = UserTypeSerializer(data=self.primary_user_type)
            if serializer.is_valid():
                return serializer.save(force_insert=True)


class UserTypesAPI(object):
    class ListView(mongo.ListCreateAPIView):
        serializer_class = UserTypeSerializer
        custom_field_form = None

        def get_serializer_class(self):
            list_type = self.request.QUERY_PARAMS.get('list_type', None)
            if list_type == "simple":
                return UserTypeSimpleSerializer
            return self.serializer_class

        def get_queryset(self):
            queryset = UserTypes.objects.all()

            # if the user is anonymous, this could be the sign up event.
            # Only return user types that allow to be registered.
            if self.request.user.is_anonymous():
                queryset = queryset.filter(is_superuser=False, allow_register=True)

            filters = self.request.QUERY_PARAMS.get('filter', None)
            if filters:
                return queryset.filter(name__icontains=filters)[:10]

            return queryset

        def post(self, request, *args, **kwargs):
            # convert json string custom_field_form to object type
            
            if 'custom_field_form' in request.DATA:
                self.custom_field_form = request.DATA['custom_field_form']
                del request.DATA['custom_field_form']
            return super(UserTypesAPI.ListView, self).post(request, *args, **kwargs)

        def post_save(self, obj, created=False):
            if self.custom_field_form:
                serializer = FormSchemaSerializer(data={'field_groups': self.custom_field_form})
                if serializer.is_valid():
                    form_object = serializer.save(force_insert=True)
                    obj.custom_field_form = form_object
                    obj.save()

    class ItemView(mongo.RetrieveUpdateDestroyAPIView):
        serializer_class = UserTypeSerializer
        queryset = UserTypes.objects.all()
        custom_field_form = None

        def put(self, request, *args, **kwargs):
            # convert json string custom_field_form to object type
            obj = self.get_object()
            if hasattr(obj, 'custom_field_form'):
                delattr(obj, 'custom_field_form')
                obj.save()
            if 'custom_field_form' in request.DATA:
                self.custom_field_form = json.loads(request.DATA['custom_field_form'])
                del request.DATA['custom_field_form']

            return super(UserTypesAPI.ItemView, self).put(request, *args, **kwargs)

        def post_save(self, obj, created=False):
            if self.custom_field_form:
                serializer = FormSchemaSerializer(data={'field_groups': self.custom_field_form})
                if serializer.is_valid():
                    form_object = serializer.save(force_insert=True)
                    obj.custom_field_form = form_object
                    obj.save()


class UserTypeFormData(mongo.GenericAPIView):
    def get(self, request, *args, **kwargs):
        records = []
        if 'usertype_id' in kwargs and kwargs['usertype_id'] is not None:
            usertype_id = kwargs['usertype_id']
            users = User.objects.filter(user_types__icontains=usertype_id)
        else:
            users = User.objects.all()

        for user in users:
            serializer = UserFormDataSerializer(user)
            custom_fields = {}
            #add custom fields if the user has some
            if user.custom_field_form:
                frm = FormSchema.objects.get(id=user.custom_field_form.id)
                groups = frm.convert_to_json()['field_groups']
                for grp in groups:
                    for fld in grp['fields']:
                        custom_fields[fld['name']] = fld['value']

            data = dict(serializer.data.items() + custom_fields.items())

            records.append(data)

        return Response(records)


class SaveUserFormData(mongo.ListCreateAPIView):
    serializer_class = FormDataSerializer
    queryset = FormData.objects.all()
    obj_id = None

    def post(self, request, *args, **kwargs):
        self.obj_id = kwargs['obj_id']
        form_schema = []
        for id in request.DATA.get('ids'):
            form_schema.append(FormSchema.objects.get(id=id).convert_to_json())

        data = {
            'form_schema': form_schema,
            'user': User.objects.get(id=self.obj_id).id,
            'data': {}
        }
        for fg in request.DATA.get('fieldGroups'):
            for field in fg['fields']:
                key = fg['name'] + ' - ' + field['name']
                data['data'][key] = field['value']
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save(force_insert=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserFormData(mongo.GenericAPIView):
    def get(self, request, *args, **kwargs):
        records = []
        if 'obj_id' in kwargs and kwargs['obj_id'] is not None:
            try:
                object_list = FormData.objects.filter(user=kwargs['obj_id'])
            except FormData.DoesNotExist:
                object_list = None
        else:
            object_list = FormData.objects.all()

        if object_list is not None:
            for obj in object_list:
                data = {
                    'user': obj.user.email
                }

                for k in obj.data:
                    data[k] = obj.data[k]

                records.append(data)

        return Response(records)
