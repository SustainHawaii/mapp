from rest_framework import status
from mongoengine.errors import NotUniqueError
from rest_framework.response import Response
from rest_framework_mongoengine import generics as Mongo
from maps.custom_form.models import FormSchema, FormData
from maps.custom_form.serializers import FormSchemaSerializer, FormDataSerializer
from maps.locations.serializers import LocationSerializer, LocationTypeSerializer
from maps.locations.serializers import LocationSimpleSerializer, LocationTypeSimpleSerializer
from maps.locations.models import Location, LocationType
from maps.categories.models import Taxonomy, Categories
from pygeocoder import Geocoder
from geojson import Point
from django.conf import settings
import requests
from rest_framework.decorators import api_view
from maps.core import api
from itertools import chain
import json
import collections
import operator
from utils import save_thumb, save_image
from django.http import HttpResponse
from bson import json_util
from mappweb.templatetags.mapp_tags import check_permission
from maps.core.views import LinkBuilder


@api_view(['GET'])
def get_map_point(request, id):
    locs = Location.objects.filter(id=id)

    # create a custom format
    return Response(build_geojson_for_googlemaps(locs))


@api_view(['GET'])
def get_map_points(request):
    """build the custom format that google maps wants"""
    locs = Location.objects.all()

    # see if we got any query strings
    query = request.GET.get('q', None)
    loc_type = request.GET.get('loc_type', None)

    if query:
        locs = locs.filter(name__icontains=query)
    if loc_type:
        locs = locs.filter(location_type=loc_type)

    # create a custom format
    return Response(build_geojson_for_googlemaps(locs))


def build_geojson_for_googlemaps(locs):
    """pass in a iterable of locations
    or location like data... i.e. external data imports
    this function attempts to convert whatever has a close enough format
    skipping over anything that doesn't have the correct properties"""
    features = []
    for loc in locs:

        if (hasattr(loc, "points") or
                (hasattr(loc, "geometry_type") and hasattr(loc, "coordinates"))):

            name = loc.name if hasattr(loc, "name") else ""
            description = loc.description if hasattr(
                loc, "description") else ""
            if hasattr(loc, "formatted_address"):
                formatted_address = loc.formatted_address
            else:
                formatted_address = ""
            #add location type
            loc_type =""
            if hasattr(loc, "location_type"):
                if loc.location_type: 
                    loc_type = loc.location_type.name
            #add last updated
            last_updated =""
            if hasattr(loc, "last_updated"):
                last_updated = loc.last_updated
            #add claimed
            claimed = ""
            if hasattr(loc, "claimed"):
                claimed = loc.claimed

            props = {
                "name": name,
                "description": description,
                "id": str(loc.id),
                "formatted_address": formatted_address,
                "loc_type": loc_type,
                "last_updated" : last_updated,
                "claimed" : claimed,
            }

            # Get the icon url
            if(hasattr(loc, "location_type")):
                # system locations
                if (loc.location_type
                        and hasattr(loc.location_type, "icon_url")
                        and loc.location_type.icon_url):

                    props["icon"] = loc.location_type.icon_url
            elif (hasattr(loc, "icon_url")):
                props["icon"] = loc.icon_url

            if hasattr(loc, "image_url") and loc.image_url:
                props["image"] = loc.image_url

            # get geometry
            if (hasattr(loc, "points")):
                if not loc.points:
                   continue 
                #    geocoded_addr = verify_address(loc.formatted_address)
                #    if geocoded_addr != 'Error':
                #        loc.points = geocoded_addr
                #        loc.save()

                geometry = loc.points
            elif (hasattr(loc, "geometry_type") and
                  hasattr(loc, "coordinates")):
                geometry = {"type": loc.geometry_type,
                            "coordinates": loc.coordinates
                            }

            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": props
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }


class MapSearch(Mongo.MongoAPIView):

    def get(self, request, *args, **kwargs):
        filters = {}
        tags = ''
        category = ''

        # see if we got any query strings
        query = request.GET.get('q', None)
        loc_type = request.GET.getlist('loc_type[]', None)
        tags = request.GET.get('tags', None)
        if tags:
            tags = json.loads(tags)
        category = request.GET.getlist('category[]', None)
        if query:
            filters['name__icontains'] = query
        locs = Location.objects.filter(**filters)
        print('category is: ', category)
        if loc_type:
            locs = locs.filter(location_type__in=loc_type)
        if category:
            cat_tags = []
            if type(category) != list:
                category = [category]
            for cat in category:
                for tag in api.taxonomy_tags.get(id=cat):                    
                    print("tag found:", tag)
                    cat_tags.append(tag['name'])
        
        if tags and category:            
            if type(tags) != list:
                tags = [tags]
            tags = list(set(tags) & set(cat_tags))
        elif category:
            tags = list(set(cat_tags))
        print("tags == ",tags)

        if tags or category:
            q = Location.objects.none()
            for tag in tags:
                q = chain(q, locs.filter(tags__icontains=tag))
            locs = set(q)
        count = len(locs)

        if count  > 500:
            locs = locs[:499]
        if count:
            data = build_geojson_for_googlemaps(locs)            
            data['features'][0]['properties']['count'] = count        
            return Response(data)
        return Response("None found")


class AddLocation(Mongo.ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def pre_save(self, obj):
        address = (self.request.DATA['address1'] + ", " + self.request.DATA['zip'],
                   self.request.DATA['city'],
                   self.request.DATA['state'])

        geocoded_addr = verify_address(address)
        if geocoded_addr != 'Error':
            obj.points = geocoded_addr

        # create new organization
        try:
            create_org(self.request, obj)
        except Exception as e:
            print e

    def post(self, request, *args, **kwargs):
        #make sure this is set as post_save checks for it
        self.custom_field_form = None
        if 'custom_field_form' in request.DATA:
            self.custom_field_form = json.loads(request.DATA['custom_field_form'])
            del request.DATA['custom_field_form']

        try:
            return self.create(request, *args, **kwargs)
        except NotUniqueError:
            return Response({'error': 'This name is already taken'}, status=status.HTTP_400_BAD_REQUEST)
            

    def post_save(self, obj, created=False):
        if not created:
            return
        f = self.request.FILES.get('file', None)
        save_image(f, obj, 'image', 'name', 'location/')

        if self.custom_field_form:
            serializer = FormSchemaSerializer(
                data=self.custom_field_form)
            if serializer.is_valid():
                form_object = serializer.save(force_insert=True)
                obj.custom_field_form = form_object
                obj.save()

    serializer_class = LocationSerializer
    queryset = Location.objects.all()

    def get_serializer_class(self):
        list_type = self.request.QUERY_PARAMS.get('list_type', None)
        if list_type == "simple":
            return LocationSimpleSerializer
        return self.serializer_class

    def get_paginate_by(self):
        if self.request.accepted_renderer.format == 'html':
            return 20
        return 100


def verify_address(data):
    try:
        results = Geocoder('AIzaSyDDLAMji-hY20cbBfOkB_88mEBtZxnerA8').geocode(data)
        #results = Geocoder().geocode(data)
        if results.coordinates:
            # Geocode.coordinates are lat, long, but we need long, lat
            return Point((results.longitude, results.latitude))
        else:
            return "Error"
    except Exception as e:
        print e
        return "Error"


class UpdateLocation(Mongo.RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer
    queryset = Location.objects.all()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.tags and self.object.tags != u'null' and self.object.custom_field_form:
            self.refresh_forms(self.object)
        return self.retrieve(request, *args, **kwargs)

    def validate_tag(self, t):
        if not t:
            return False
        if not t.custom_field_form:
            return False
        return True

    def refresh_forms(self, obj):
        obj_field_groups = obj.custom_field_form.field_groups
        new_field_groups = []
        tags = [t for t in obj.tags if self.validate_tag(t)]
        for tag in tags:
            for fg in tag.custom_field_form.field_groups:
                fg['id'] = 'tag';
                fields = fg['fields']
                obj_fields = [g for g in obj_field_groups if g['name'] == fg['name']]
                if obj_fields:
                    obj_fields = obj_fields[0]['fields']
                    for field in fields:
                        for obj_field in obj_fields:
                            if obj_field['name'] == field['name'] and obj_field['value']:
                                field['value'] = obj_field['value']
                new_field_groups.append(fg)

        location_type = LocationType.objects.filter(id=obj.location_type.id)[0]
        try:
            location_type = location_type.custom_field_form.field_groups
            for fg in location_type:
                fg['id'] = 'locationtype'
                fields = fg['fields']
                obj_fields = [g for g in obj_field_groups if g['name'] == fg['name']]
                if obj_fields:
                    obj_fields = obj_fields[0]['fields']
                    for field in fields:
                        for obj_field in obj_fields:
                            if obj_field['name'] == field['name'] and obj_field['value']:
                                field['value'] = obj_field['value']
                new_field_groups.append(fg)
        except AttributeError:
            print('LocationType has no CustomForms ')
        obj.custom_field_form.field_groups = new_field_groups
        obj.custom_field_form.save()
        obj.save()
        
    def pre_save(self, obj):
        address = (self.request.DATA['address1'] + ", " +
                   self.request.DATA['zip'],
                   self.request.DATA['city'],
                   self.request.DATA['state'])
        

        geocoded_addr = verify_address(address)
        if geocoded_addr != 'Error':
            obj.points = geocoded_addr

        # create new organization
        try:
            create_org(self.request, obj)
        except Exception as e:
            print e

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.custom_field_form:
            delattr(obj, 'custom_field_form')
            obj.save()
        self.custom_field_form = None
        if 'custom_field_form' in request.DATA:
            self.custom_field_form = json.loads(
                request.DATA['custom_field_form'])
            del request.DATA['custom_field_form']
        self.tags = None
        if 'tags' in request.DATA:
            self.tags = json.loads(request.DATA['tags'])
            print("tags", self.tags)
            del request.DATA['tags']
        return super(UpdateLocation, self).put(request, *args, **kwargs)

    def post_save(self, obj, created=False):
        f = self.request.FILES.get('file', None)
        save_image(f, obj, 'image', 'name', 'location/')
        if self.custom_field_form:
            serializer = FormSchemaSerializer(
                data=self.custom_field_form)
            if serializer.is_valid():
                form_object = serializer.save(force_insert=True)
                obj.custom_field_form = form_object
                obj.save()
        if self.tags:
            for tag in self.tags:
                print tag
                Categories.objects(id=tag['id']).update_one(push__tagged=obj)


def create_org(request, obj):
    org = json.loads(request.DATA['org'])[0]
    if org['id'] == org['text']:
        data = {}
        data['name'] = org['text']
        data['address'] = request.DATA.get('org_address', '')
        data['city'] = request.DATA.get('org_city', '')
        data['state'] = request.DATA.get('org_state', '')
        data['zip'] = request.DATA.get('org_zip', '')
        data['phone'] = request.DATA.get('org_phone', '')
        data['website'] = request.DATA.get('org_website', '')
        data['privacy'] = 'Everyone'

        new_org = True
        req = requests.get(settings.CORE_API_URL + '/org/')
        for i in req.json():
            if i['name'] == org['text']:
                new_org = False
                break

        if new_org:
            req = requests.post(settings.CORE_API_URL + '/org/', data=data)
            res = req.json()
            obj.org = request.DATA['org'].replace(
                'id\":\"' + org['id'], 'id\":\"' + str(res['id']))
        request.DATA.pop('org', None)


class AddLocationType(Mongo.ListCreateAPIView):
    serializer_class = LocationTypeSerializer
    queryset = LocationType.objects.all()
    custom_fields = None
    taxonomies = None

    def get_serializer_class(self):
        list_type = self.request.QUERY_PARAMS.get('list_type', None)
        if list_type == "simple":
            return LocationTypeSimpleSerializer
        return self.serializer_class

    def post(self, request, *args, **kwargs):
        # convert json string custom_fields to object type
        if 'custom_fields' in request.DATA:
            self.custom_fields = json.loads(request.DATA['custom_fields'])
            del request.DATA['custom_fields']
        if 'custom_field_form' in request.DATA:
            del request.DATA['custom_field_form']
        if 'taxonomies' in request.DATA:
            self.taxonomies = json.loads(request.DATA['taxonomies'])
            del request.DATA['taxonomies']                                         
        return super(AddLocationType, self).post(request, *args, **kwargs)

    def post_save(self, obj, created=False):
        if not created:
            return
        f = self.request.FILES.get('file', None)
        save_thumb(f, obj, 'icon', 'name', 'location_type/')

        if self.custom_fields:
            serializer = FormSchemaSerializer(
                data={'field_groups': self.custom_fields})
            if serializer.is_valid():
                form_object = serializer.save(force_insert=True)
                obj.custom_field_form = form_object
                obj.save()
        if self.taxonomies:
            obj.taxonomies = self.taxonomies
            obj.save()

    def get_paginate_by(self):
        return 100


class UpdateLocationType(Mongo.RetrieveUpdateDestroyAPIView):
    serializer_class = LocationTypeSerializer
    queryset = LocationType.objects.all()
    custom_fields = None
    taxonomies = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.taxonomies:
            self.refresh_categories(self.object)
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def refresh_categories(self, obj):
        try:
            obj_field_groups = obj.custom_field_form.field_groups
        except AttributeError:
            return
        # retain location specific custom forms

        tmp = [fg for fg in obj_field_groups if fg['id'] != "category"]
        # remove duplicates
        new_field_groups = []
        [new_field_groups.append(fg) for fg in tmp if fg not in new_field_groups]
        categories = Taxonomy.objects.filter(id__in=obj.taxonomies)
        categories = [cat for cat in categories if cat.custom_field_form.field_groups]

        for cat in categories:
            for fg in cat.custom_field_form.field_groups:
                fg['id'] = 'category';
                fields = fg['fields']
                obj_fields = [g for g in obj_field_groups if g['name'] == fg['name']]
                if obj_fields:
                    obj_fields = obj_fields[0]['fields']
                    for field in fields:
                        for obj_field in obj_fields:
                            if obj_field['name'] == field['name'] and obj_field['value']:
                                field['value'] = obj_field['value']
                new_field_groups.append(fg)

        obj.custom_field_form.field_groups = new_field_groups
        obj.custom_field_form.save()
            
    def put(self, request, *args, **kwargs):
        # convert json string custom_fields to object type
        obj = self.get_object()
        if hasattr(obj, 'custom_field_form'):
            delattr(obj, 'custom_field_form')
            obj.save()
            if 'custom_field_form' in request.DATA:
                self.custom_field_form = json.loads(request.DATA['custom_field_form'])
                del request.DATA['custom_field_form']
        if 'taxonomies' in request.DATA:
            self.taxonomies = json.loads(request.DATA['taxonomies'])
            del request.DATA['taxonomies']
        return super(UpdateLocationType, self).put(request, *args, **kwargs)

    def post_save(self, obj, created=False):
        f = self.request.FILES.get('file', None)
        save_thumb(f, obj, 'icon', 'name', 'location_type/')

        if self.custom_field_form:
            serializer = FormSchemaSerializer(
                data=self.custom_field_form, many=False)
            if serializer.is_valid():
                form_object = serializer.save(force_insert=True)
                obj.custom_field_form = form_object
                obj.save()
        if self.taxonomies:
            obj.taxonomies = self.taxonomies
            obj.save()


class SaveLocationFormData(Mongo.ListCreateAPIView):
    serializer_class = FormDataSerializer
    queryset = FormData.objects.all()
    location_id = None

    def post(self, request, *args, **kwargs):
        self.location_id = kwargs['location_id']
        form_schema = []
        for id in request.DATA.get('ids'):
            form_schema.append(FormSchema.objects.get(id=id).convert_to_json())
        data = {
            'form_schema': form_schema,
            'location': Location.objects.get(id=self.location_id),
            'data': {}
        }
        for fg in request.DATA.get('fieldGroups'):
            for field in fg['fields']:
                key = fg['name'] + '_' + field['name']
                data['data'][key] = field['value']
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save(force_insert=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationFormData(Mongo.GenericAPIView):

    def get(self, request, *args, **kwargs):
        records = []
        if 'location_id' in kwargs and kwargs['location_id'] is not None:
            try:
                object_list = FormData.objects.filter(
                    location=kwargs['location_id'])
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


class LocationTypeFormData(Mongo.GenericAPIView):

    def get(self, request, *args, **kwargs):
        records = []
        if 'locationtype_id' in kwargs and kwargs['locationtype_id'] is not None:
            try:
                locations = Location.objects.filter(
                    location_type=kwargs['locationtype_id'])
                object_list = FormData.objects.filter(location__in=locations)
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


def clean_point():
    clean_p = []
    for data_v in requests.get("http://127.0.0.1:8000/api/v1/points/").json['results']:
        point = {
            'longitude': float(data_v['longitude']),
            'latitude': float(data_v['latitude']),
            'type': data_v['types'][0]
        }
        clean_p.append(point)
    return clean_p


def add_address(id, data):
    loc = Location.objects.get(id=id)
    loc.points = dict(data)
    loc.save()

def get_claim_user(id):
    try:
        return request.user.__class__.objects.get(id=q.also_editable_by).name
    except:
        return ''

def locations_datatable(request):
    start = int(request.GET['iDisplayStart'])
    length = int(request.GET['iDisplayLength'])
    sEcho = int(request.GET['sEcho'])

    if 'Admin' in [ut.name for ut in request.user.user_types]:
        query = Location.objects.all()
    else:
        org = request.user.organization
        query = Location.objects.filter(org__contains=str(org.id))
    total = query.count()

    search_param = request.GET.get('sSearch', None)
    if search_param:
        loc_type = LocationType.objects.filter(name__icontains=search_param)
        q = chain(
            query.filter(name__icontains=search_param),
            query.filter(created__icontains=search_param),
            query.filter(last_updated__icontains=search_param),
            query.filter(location_type__in=loc_type),
        )
        query = list(set(q))
    total_display = len(query)

    def check_loc_type(lt):
        if lt:
            return lt.name
        return ''
    Qry = collections.namedtuple(
        'Qry', 'id name loc_type created claimed_by last_updated created_by')
    query = [
        Qry(
            id=str(q.id),
            name=q.name,
            loc_type=check_loc_type(q.location_type),
            created=q.created.strftime("%Y-%m-%d"),
            claimed_by=get_claim_user(q.also_editable_by),
            last_updated=q.last_updated.strftime("%Y-%m-%d"),
            created_by=q.created_by
        )
        for q in query if q]

    cols = ['name', 'loc_type', 'created', 'claimed_by', 'last_updated', 'created_by']
    sort_col = request.GET.get('iSortCol_0', None)
    sort_order = request.GET.get('sSortDir_0', None)
    if sort_col:
        sort_col = int(sort_col)
        if sort_col < 4:
            is_reverse = sort_order == 'desc'
            query = sorted(
                query, key=operator.attrgetter(cols[sort_col]), reverse=is_reverse)

    query = query[start:start + length]


    # has edit permission
    OtherEdit = request.user.has_edit_other_permission("locations") 
    OtherDel = request.user.has_delete_other_permission("locations") 
    OwnEdit = request.user.has_edit_own_permission("locations") 
    OwnDel = request.user.has_delete_own_permission("locations") 

    if any([OtherEdit, OtherDel, OwnEdit, OwnDel]):
        link_builder = LinkBuilder(request.user,
                                "/maps-admin/locations-update/",
                                "locations")
        query = [
            (
                link_builder.view_link(q),
                q.loc_type,
                q.created,
                q.claimed_by,
                q.last_updated,
                link_builder.edit_link(q) +
                link_builder.del_link(q)
            ) for q in query
        ]
    response = {
        "aaData": query,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total_display,
        "sEcho": sEcho,
    }
    response = json.dumps(response, default=json_util.default)

    return HttpResponse(
        response,
        content_type='application/json'
    )
