import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from mongoengine.errors import NotUniqueError
from maps.custom_form.models import FormData
from maps.custom_form.serializers import FormSchemaSerializer
from itertools import chain
from serializers import *
from rest_framework_mongoengine import generics as mongo
from rest_framework.response import Response
from maps.locations.models import Location
from .models import Categories, Taxonomy
from maps.data_import.models import Data, DataImport
from maps.data_import.serializers import DataSerializer


class AddCategories(mongo.ListCreateAPIView):
    serializer_class = CategoriesSerializer
    queryset = Categories.objects.all()
    custom_field_form = None

    def get_serializer_class(self):
        list_type = self.request.QUERY_PARAMS.get('list_type', None)
        if list_type == "simple":
            return CategoriesSimpleSerializer
        return self.serializer_class

    def get_queryset(self):
        filters = self.request.QUERY_PARAMS.get('filter', None)
        forid = self.request.QUERY_PARAMS.get('forid', None)
        cls = self.request.QUERY_PARAMS.get('cls', None)

        if filters:
            return Categories.objects.filter(name__icontains=filters)[:10]

        if forid and cls:
            return Categories.for_object_id(forid, cls)

        return Categories.objects.all()


    def post(self, request, *args, **kwargs):
        # convert json string custom_field_form to object type
        if 'custom_field_form' in request.DATA:
            self.custom_field_form = json.loads(request.DATA['custom_field_form'])
            del request.DATA['custom_field_form']

        # convert object taxonomies to json string
        if 'taxonomies' in request.DATA:
            request.DATA['taxonomies'] = json.dumps(request.DATA['taxonomies'])
        try:
            return super(AddCategories, self).post(request, *args, **kwargs)
        except NotUniqueError:
            return JsonResponse({"error":"NotUniqueError"})

    def post_save(self, obj, created=False):
        if self.custom_field_form:
            serializer = FormSchemaSerializer(data={'field_groups': self.custom_field_form})
            if serializer.is_valid():
                form_object = serializer.save(force_insert=True)
                obj.custom_field_form = form_object
                obj.save()


class UpdateCategory(mongo.RetrieveUpdateDestroyAPIView):
    serializer_class = CategoriesSerializer
    queryset = Categories.objects.all()
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

        # convert object taxonomies to json string
        if 'taxonomies' in request.DATA:
            request.DATA['taxonomies'] = json.dumps(request.DATA['taxonomies'])
        try:
            return super(UpdateCategory, self).put(request, *args, **kwargs)
        except NotUniqueError:
            return JsonResponse({"error":"NotUniqueError"})        

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def post_save(self, obj, created=False):
        if self.custom_field_form:
            serializer = FormSchemaSerializer(data={'field_groups': self.custom_field_form})
            if serializer.is_valid():
                form_object = serializer.save(force_insert=True)
                obj.custom_field_form = form_object
                obj.save()


class AddTaxonomy(mongo.ListCreateAPIView):
    serializer_class = TaxonomySerializer
    queryset = Taxonomy.objects.all()
    custom_field_form = None


    def get_queryset(self):
        filters = self.request.QUERY_PARAMS.get('filter', None)
        if filters:
            return Taxonomy.objects.filter(name__icontains=filters)[:10]

        return Taxonomy.objects.all()

    def get_serializer_class(self):
        list_type = self.request.QUERY_PARAMS.get('list_type', None)
        if list_type == "simple":
            return TaxonomySimpleSerializer
        return self.serializer_class

    def post(self, request, *args, **kwargs):
        # convert json string custom_field_form to object type
        if 'custom_field_form' in request.DATA:
            self.custom_field_form = json.loads(request.DATA['custom_field_form'])
            del request.DATA['custom_field_form']

        if 'inherit' in request.DATA and request.DATA['inherit'] is None:
            del request.DATA['inherit']
        try:
            return super(AddTaxonomy, self).post(request, *args, **kwargs)
        except NotUniqueError:
            return JsonResponse({"error":"NotUniqueError"})        

    def post_save(self, obj, created=False):
        # MongoEngine ReferenceField cannot accept None Type. So have to
        # do the trick here to remove the 'inherit'.
        if 'inherit' not in self.request.DATA:
            del obj.inherit
            obj.save()

        if self.custom_field_form:
            serializer = FormSchemaSerializer(data={'field_groups': self.custom_field_form})
            if serializer.is_valid():
                form_object = serializer.save(force_insert=True)
                obj.custom_field_form = form_object
                obj.save()


class UpdateTaxonomy(mongo.RetrieveUpdateDestroyAPIView):
    serializer_class = TaxonomySerializer
    queryset = Taxonomy.objects.all()
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
        else:
            if hasattr(obj, 'custom_field_form'):
                obj.custom_field_form.delete()
                delattr(obj, 'custom_field_form')
        if 'inherit' in request.DATA and request.DATA['inherit'] is None:
            del request.DATA['inherit']
        try:
            return super(UpdateTaxonomy, self).put(request, *args, **kwargs)
        except NotUniqueError:
            return JsonResponse({"error":"NotUniqueError"})

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def post_save(self, obj, created=False):
        # MongoEngine ReferenceField cannot accept None Type. So have to
        # do the trick here to remove the 'inherit'.
        if 'inherit' not in self.request.DATA:
            del obj.inherit
            obj.save()

        if self.custom_field_form:
            serializer = FormSchemaSerializer(data={'field_groups': self.custom_field_form})
            if serializer.is_valid():
                form_object = serializer.save(force_insert=True)
                obj.custom_field_form = form_object
                obj.save()


class GetTaxonomyTags(mongo.ListAPIView):
    serializer_class = CategoriesSerializer

    def get_queryset(self):
        cat = []
        tax_id = self.kwargs['id']
        for c in Categories.objects.all():
            if c.taxonomies:
                tax = json.loads(c.taxonomies)
                if tax_id in tax and tax[tax_id]:
                    cat.append(c)
        return cat


class CategoryExternalData(mongo.ListAPIView):
    serializer_class = DataSerializer

    def get_queryset(self):
        cat_id = self.kwargs['id']
        limit = self.request.QUERY_PARAMS.get('limit', None)
        object_list = Data.objects.none()

        try:
            cat = Categories.objects.get(id=cat_id)
            import_ids = [] 
            for obj in Categories.objects_with(cat.name):
                #if it's DataImport, get the associated data
                if type(obj) == DataImport:
                    import_ids.append(str(obj.id))
            
            if import_ids:
                object_list = Data.objects.filter(import_id__in=import_ids)

                if limit:
                    object_list = object_list[:int(limit)]

        except Categories.DoesNotExist:
            pass

        return object_list



class CategoryFormData(mongo.GenericAPIView):
    def get(self, request, *args, **kwargs):
        records = []
        if 'category_id' in kwargs and kwargs['category_id'] is not None:
            cat_id = kwargs['category_id']
            try:
                cat = Categories.objects.get(id=cat_id)
                object_list = FormData.objects.none()
                for loc in Categories.objects_with(cat.name):
                    if type(loc) == Location:
                        object_list = chain(object_list, FormData.objects.filter(location=loc))
            except FormData.DoesNotExist:
                object_list = None
        else:
            object_list = FormData.objects.all()

        if object_list is not None:
            for obj in object_list:
                data = {
                    'location': obj.location.name
                }

                for k in obj.data:
                    data[k] = obj.data[k]

                records.append(data)

        return Response(records)


class TaxonomyFormData(mongo.GenericAPIView):
    def get(self, request, *args, **kwargs):
        records = []
        if 'taxonomy_id' in kwargs and kwargs['taxonomy_id'] is not None:
            tax_id = self.kwargs['taxonomy_id']
            try:
                cat = []
                for c in Categories.objects.all():
                    tax = json.loads(c.taxonomies)
                    if tax_id in tax and tax[tax_id]:
                        cat.append(c)
                object_list = FormData.objects.none()
                for c in cat:
                    for loc in Location.objects.filter(tags__icontains=c.name):
                        object_list = chain(object_list, FormData.objects.filter(location=loc))
            except FormData.DoesNotExist:
                object_list = None
        else:
            object_list = FormData.objects.all()

        object_list = set(object_list)
        if object_list is not None:
            for obj in object_list:
                data = {
                    'location': obj.location.name
                }

                for k in obj.data:
                    data[k] = obj.data[k]

                records.append(data)

        return Response(records)

@login_required(login_url='/')
def category_delete_view(request, id):
    try:
        cat = Taxonomy.objects.get(id=id)
        cat.delete()
    except Taxonomy.DoesNotExist:
        print('No Category to Delete')
    return redirect('/maps-admin/categories/')

@login_required(login_url='/')
def tag_delete_view(request, id):
    try:
        cat = Categories.objects.get(id=id)
        cat.delete()
    except Categories.DoesNotExist:
        print('No Category to Delete')
    return redirect('/maps-admin/categories/')


