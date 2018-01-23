from django.template import RequestContext
import json
import geojson
import itertools
from mongoengine import Document
from mongoengine import ValidationError
from rest_framework import renderers
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import shapefile
import demjson
import struct
import zipfile
from mappweb.settings import DATA_IMPORT_OPTIONS, DATA_NORMALIZATION_FIELDS
from maps.categories.models import Categories, Taxonomy
from maps.users.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render_to_response, redirect
from maps.locations.models import LocationType, Location
from maps.org.models import Organization
from serializers import *
from maps.locations.serializers import LocationSerializer
import csv
import requests
import datetime
import dateutil.parser as dateparser
import os
from utils import make_temp_directory, convert
from django.conf import settings
import mongoengine
from mongoengine.queryset import NotUniqueError
from mongoengine.fields import ReferenceField, BooleanField, DateTimeField
from mongoengine.fields import StringField
from pygeocoder import Geocoder

role = 'maps-admin'
template_base_path = 'maps-admin/settings/'


def init_data():
    data = {
        'role': role,
        'options': DATA_IMPORT_OPTIONS,
        'filetypes_can_modify': ['0','1'],
    }
    return data


def settings_import_view(request):
    data = init_data()

    # delete import
    obj_id = request.GET.get('delete', None)
    if obj_id:
        obj = DataImport.objects.get(id=obj_id)
        # delete file
        if obj.upload_file:
            try:
                os.remove(obj.upload_file)
            except:
                pass
        # delete data
        Data.objects.filter(import_id=obj_id).delete()
        # delete instance
        obj.delete()

        return redirect('/maps-admin/settings-import')

    data['imports'] = DataImport.objects.all()
    return render_to_response('maps-admin/settings/settings-import.html', data, context_instance=RequestContext(request))


class SettingsImportFileView(GenericAPIView):
    renderer_classes = (renderers.TemplateHTMLRenderer,)
    template_name = template_base_path + 'settings-importfile.html'

    def get(self, request, *args, **kwargs):
        data = init_data()

        # update view context
        obj_id = request.GET.get('id', None)
        step = request.GET.get('step', None)
        if obj_id:
            data['object'] = DataImport.objects.get(id=obj_id)
            dataset = Data.objects.filter(import_id=obj_id)[:5]
            data['fields'] = dataset[0]._fields_ordered
            data['normalized_fields'] = DATA_NORMALIZATION_FIELDS
            data['dataset'] = dataset
            data['step'] = step if step else 'table'
            data['import_id'] = obj_id

        if 'fields' in data:
            data['fields'] = [
                x for x in data['fields'] if x not in ('id', 'import_id')]
      
            data['numfields'] = [x for x in data['fields']
                                 if isinstance(getattr(dataset[0], x), (int, long, float))]

        return Response(data=data)

    def post(self, request, *args, **kwargs):
        data = init_data()
        obj = None
        # update view context
        obj_id = request.GET.get('id', None)

        if obj_id:
            obj = DataImport.objects.get(id=obj_id)
            data['object'] = obj
            dataset = Data.objects.filter(import_id=obj_id)
            data['fields'] = dataset[0]._fields_ordered
            data['dataset'] = dataset
            data['step'] = 'table'

        request.POST['last_updated'] = datetime.datetime.now()

        if obj:
            request.POST['upload_file'] = obj.upload_file
            serializer = DataImportSerializer(data=request.POST, instance=obj)
        else:
            serializer = DataImportSerializer(
                data=request.POST, remove_fields=['id'])

        if serializer.is_valid():
            serializer.errors['msg'] = []
            replace_dup = serializer.object.duplicate_content == '0'

            # static file
            if serializer.object.upload_type == '0':
                uploaded_file = request.FILES.get('upload_file', None)

                # if have new file uploaded
                if uploaded_file:
                    # if have file uploaded recently, delete it before storing
                    # the new file
                    if serializer.object.upload_file:
                        os.remove(serializer.object.upload_file)

                    # save the new uploaded file
                    #path = default_storage.save(
                    #    'data_import/' + uploaded_file.name, ContentFile(uploaded_file.read()))
                    #serializer.object.upload_file = os.path.join(
                    #    settings.MEDIA_ROOT, path)

                    # CSV
                    if serializer.object.upload_format == '0':
                        try:
                            # need to save the Data Import first
                            serializer.save()
                            parse_csv(uploaded_file, serializer.object, Data,
                                      int(request.POST.get('start_row', 1)), replace_dup)
                        except Exception as e:
                            serializer.errors['upload_file_error'] = [
                                'Invalid CSV file.']

                    # JSON
                    if serializer.object.upload_format == '1':
                        try:
                            serializer.save()
                            contents = ''
                            for line in uploaded_file:
                                contents += line
                            demjson.decode(contents)
                            contents = json.loads(contents)
                            contents = flatten_json(contents)
                            parse_json(
                                contents, serializer.object, Data, replace_dup)
                        except Exception as e:
                            print e
                            serializer.errors['upload_file_error'] = [
                                'Invalid JSON file.', ': '.join(e)]
                    # shapefile (zipped)
                    elif serializer.object.upload_format == '2':
                        with make_temp_directory() as temp_dir:
                            missing_require_files = False
                            require_files = {
                                '.dbf': None,
                                '.shp': None,
                                '.shx': None
                            }

                            try:
                                # extract the zip file
                                with zipfile.ZipFile(uploaded_file, 'r') as z:
                                    for name in z.namelist():
                                        if os.path.splitext(name)[1] in ('.dbf', '.shp', '.shx'):
                                            require_files[
                                                os.path.splitext(name)[1]] = name
                                            z.extract(name, temp_dir)

                            except zipfile.BadZipfile:
                                serializer.errors['upload_file_error'] = [
                                    'Uploaded file is not a zip file.']
                                serializer.errors['msg'].append(
                                    'Uploaded file is not a zip file.')

                            # check missing require files
                            for filetype in require_files:
                                if require_files[filetype] is None:
                                    missing_require_files = True
                                    break

                            if missing_require_files:
                                serializer.errors['upload_file_error'] = [
                                    'Missing required files. Must provide .shp, .dbf and .shx files.']
                                serializer.errors['msg'].append(
                                    'Missing required files. Must provide .shp, .dbf and .shx files.')

                            else:
                                # need to save the Data Import first
                                serializer.save()

                                try:
                                    # read the shapefile
                                    reader = shapefile.Reader(
                                        temp_dir + '/' + require_files['.shp'])
                                    fields = reader.fields[1:]
                                    field_names = [field[0]
                                                   for field in fields]
                                    buffer = []
                                    for sr in reader.shapeRecords():
                                        atr = dict(zip(field_names, sr.record))
                                        geom = sr.shape.__geo_interface__
                                        buffer.append(
                                            dict(type="Feature", geometry=geom, properties=atr))

                                    # split the record and save into DB
                                    for rec in buffer:
                                        model = Data(
                                            import_id=str(serializer.object.id))
                                        setattr(
                                            model, 'geometry_type', rec['geometry']['type'])
                                        setattr(
                                            model, 'coordinates', rec['geometry']['coordinates'])
                                        for key in rec['properties']:
                                            setattr(
                                                model, key, rec['properties'][key])
                                        model.save()

                                except struct.error:
                                    serializer.errors['upload_file_error'] = [
                                        'Uploaded file is invalid.']
                                    serializer.errors['msg'].append(
                                        'Uploaded file is invalid.')

                    # GeoJSON
                    elif serializer.object.upload_format == '3':
                        # need to save the Data Import first
                        serializer.save()

                        contents = ''
                        for line in uploaded_file:
                            contents += line

                        contents = json.loads(contents)

                        # split the record and save into DB
                        for rec in contents['features']:
                            model = Data(import_id=str(serializer.object.id))
                            setattr(
                                model, 'geometry_type', rec['geometry']['type'])
                            setattr(
                                model, 'coordinates', rec['geometry']['coordinates'])
                            for key in rec['properties']:
                                setattr(model, key, rec['properties'][key])
                            model.save()

                elif obj:
                    serializer.save()

                # if no existing uploaded file
                elif not obj:
                    serializer.errors['upload_file_error'] = [
                        'No file uploaded.']

            # live feed
            elif serializer.object.upload_type == '1':
                err_url = 'Live feed error: Please check the upload url.'
                url = request.POST.get('upload_url', None)
                if url:
                    try:
                        req = requests.get(url)
                        if not req.status_code != '200':
                            serializer.errors['upload_url'] = [err_url]
                        else:
                            try:
                                # need to save the Data Import first
                                serializer.save()
                                if serializer.object.upload_format == '1':
                                    parse_json(
                                        req.json(), serializer.object, Data, replace_dup)
                                elif serializer.object.upload_format == '3':
                                    contents = req.json()

                                # split the record and save into DB
                                for rec in contents['features']:
                                    model = Data(
                                        import_id=str(serializer.object.id))
                                    setattr(
                                        model, 'geometry_type', rec['geometry']['type'])
                                    setattr(
                                        model, 'coordinates', rec['geometry']['coordinates'])
                                    for key in rec['properties']:
                                        setattr(
                                            model, key, rec['properties'][key])
                                    model.save()
                            except Exception as e:
                                print e
                                serializer.errors['upload_url'] = [
                                    'Invalid JSON file.', ': '.join(e)]
                    except requests.ConnectionError:
                        serializer.errors['upload_url'] = [err_url]

                else:
                    serializer.errors['upload_url'] = ['Please input url.']

        else:
            print(serializer.errors)
            msg = ["%s - %s" % (k, "".join(v)) for k, v in
                             serializer.errors.items()
                             if v]
            serializer.errors['msg'] = msg
            #serializer.errors['msg'] = ['Please correct the errors.']

        try:
            dataset = Data.objects.filter(import_id=str(serializer.object.id))
            data['fields'] = dataset[0]._fields_ordered
            data['dataset'] = dataset
        except:
            print(serializer.errors)
            if (not serializer.errors['msg']):
                msg = ["%s - %s" % (k, "".join(v)) for k, v in
                                 serializer.errors.items()
                                 if v]
                serializer.errors['msg'] = msg

        data['errors'] = serializer.errors
        success = len(serializer.errors['msg']) < 1

        if not success and not obj and serializer.object:
            if serializer.object.id:
                serializer.object.delete()

        if success:
            data['object'] = serializer.object
            data['step'] = 'normalize'
            data['normalized_fields'] = DATA_NORMALIZATION_FIELDS

            #if we have gotten this far save the tags
            update_categories(serializer.object, request.POST.get("cats"))

        else:
            data['object'] = request.POST

        if 'fields' in data:
            data['fields'] = [
                x for x in data['fields'] if x not in ('id', 'import_id')]

        return Response(data=data)

def update_categories(data_import, cats_list):
    if (not data_import): return
    #clear out all existing categories for Data Import
    Categories.remove_obj(data_import)

    #now add the Categories
    if cats_list:
        for cat_id in cats_list.split(","):
            try:
                Categories.objects.get(id=cat_id.strip()).add_object(data_import)
            except (ValidationError, Categories.DoesNotExist) as e:
                pass

def parse_csv(f, obj, model, start_row, replace_dup):
    assert issubclass(model, Document), 'Invalid model.'
    if replace_dup:
        model.objects.filter(import_id=str(obj.id)).delete()

    reader = csv.reader(f)
    count = 1
    for row in reader:
        if count < start_row:
            pass
        elif count == start_row:
            header = [strip_non_ascii(i) for i in row if i]
        else:
            try:
                data = model(import_id=str(obj.id))
                for i in range(len(row)):
                    #in case we have extra commas at the end
                    if i < len(header):
                        setattr(data, header[i], row[i])
                data.save()
            except Exception as e:
                print "error in parse csv", e
                pass
        count += 1

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def flatten_json(son):
    flat = []
    if len(son) == 1 and type(son[son.keys()[0]]) == list:
        return flatten_json(son[son.keys()[0]])
    def flatten_dict(d):
        def expand(key, value):
            if isinstance(value, dict):
                return [ (key + '_' + k, v) for k, v in flatten_dict(value).items() ]
            else:
                return [ (key, value) ]
        items = [ item for k, v in d.items() for item in expand(k, v) ]
        return dict(items)
    for d in son:
        flat.append(flatten_dict(d))
    return flat

def parse_json(json, obj, model, replace_dup):
    if replace_dup:
        model.objects.filter(import_id=str(obj.id)).delete()
    format = json[0].keys()
    id = 'id' in format
    for i in json:
        if i.keys() == format:
            if id:
                tmp = i['id']
                del(i['id'])
                i['_id_'] = tmp
            data = model(import_id=str(obj.id), **i)
            data.save()


@api_view(['GET'])
def get_fields(request):
    model = request.GET.get('model', None)
    results = []
    required_fields = []

    if model == '0':
        #TODO we could do this style to limit the fields to import
        #and to prompt the user for the required fields
        fields = Location.import_fields()
        required_fields = Location.required_import_fields()
    elif model == '1':
        fields = LocationType._fields
    elif model == '2':
        fields = User._fields        
    elif model == '3':
        fields = Taxonomy._fields
    elif model == '4':
        fields = Organization._fields
    elif model == '5':
        fields = Categories._fields

    #alphabetize
    return Response({'fields': sorted(fields.keys()),
                     'required_fields' : required_fields})


class SettingsImportSystemView(GenericAPIView):
    renderer_classes = (renderers.TemplateHTMLRenderer,)
    template_name = template_base_path + 'settings-importsystem.html'
    uploaded_file = ''

    def get(self, request):
        data = init_data()
        return Response(data=data)

    def post(self, request):
        data = init_data()
        data['errors'] = {}

        upload_type = request.POST.get('upload_type', None)
        model = request.POST.get('content_type', None)
        replace_dup = request.POST.get('duplicate_content', None) == '0'
        if model == '0':
            model = Location
            unique = 'name'
            required = ('location_type',)
            success_url = '/maps-admin/locations'
        elif model == '1':
            model = LocationType
            unique = 'name'
            required = ('name',)
            success_url = '/maps-admin/locations-types'
        elif model == '3':
            model = Taxonomy 
            unique = 'name'
            required = ('name',)
            success_url = '/maps-admin/categories'
        elif model == '4':
            model = Organization
            unique = 'name'
            required = ('name',)
            success_url = '/maps-admin/users'
        elif model == '5':
            model = Categories
            unique = 'name'
            required = ('name',)
            success_url = '/maps-admin/categories'

        # static file
        if upload_type == '0':
            self.uploaded_file = request.FILES.get('upload_file', None)

            # import csv
            format = request.POST.get('upload_format', None)
            if format in ['1', '2', '0']:
                try:
                    #print("trying to import");
                    global json
                    if(format == '1'):
                        self.uploaded_file.open()
                        fh = self.uploaded_file                        
                        f = json.loads(fh.read())
                        self.upsert(request, model, json=f)
                    elif format == '2':
                        '''Allow geojson lib to do the heavy lifting'''
                        self.uploaded_file.open()
                        fh = self.uploaded_file.file.read()
                        if ']]], [[[' in fh:
                            '''Shape > geojson file coversion seems to introduce some
                            unusual artifacts, this tries to fix that'''
                            fh = fh.replace(']]], [[[', '], [')

                        f = geojson.loads(fh)
                        self.make_locations(f, request)
                    else:
                        self.upsert(request, model)
                except (TypeError, AttributeError, ValueError) as e:
                    print ("error", e)
                    data['errors']['msg'] = e
                    data['errors']['upload_file'] = 'Import error. Please check the file.'
                    data['object'] = request.POST
                    return Response(data=data)
        # live feed
        elif upload_type == '1':
            err_url = 'Import error. Please input valid url.'
            url = request.POST.get('upload_url', None)
            if url:
                try:
                    req = requests.get(url)
                    if not req.status_code != '200':
                        data['errors']['upload_url'] = [err_url]
                        data['object'] = request.POST
                        return Response(data=data)
                    else:
                        try:
                            json = req.json()
                            self.upsert(request, model, json)
                        except Exception as e:
                            data['errors']['msg'] = e
                            data['errors']['upload_url'] = [
                                'Invalid JSON file.']
                            return Response(data=data)
                except requests.ConnectionError:
                    data['errors']['upload_url'] = [err_url]
                    data['object'] = request.POST
                    return Response(data=data)
            else:
                data['object'] = request.POST
                data['errors']['upload_url'] = [err_url]
                return Response(data=data)
        data['redirect'] = success_url
        return Response(data=data)

    def make_locations(self, f, request):
         if 'TMK' in f.get('features')[0].get('properties'):
             self.upload_tmk_data(f)
         else:
             prop_list = [j.get('properties') for j in f.get('features')]
             map = self.extract_mappings(request, file=None, model=Location, json=prop_list[0])
             obj_list = self.make_objects(prop_list, map, Location)
             for feature, obj in itertools.izip(f.get('features'), obj_list):
                 coord = feature.get('geometry').get('coordinates')
                 obj.points = coord
                 obj.save()
             return obj_list
             

    def upload_tmk_data(self, f):
        ''' Due to Ainbilities dependence on TMK 
            data it should get special treatment'''
        lt = LocationType.objects.get(name='TMK')
        for feature in f["features"]:
            try:
                location = Location()
                properties = feature["properties"]
                location.name = properties.get("MajorOwner", "NoMajorOwner")+unicode(properties.get("TMK"))
                location.points = feature.get("geometry").get("coordinates")
                location.location_type = lt
                location.save()
            except (mongoengine.ValidationError, mongoengine.OperationError) as e:
                if e == mongoengine.OperationError:
                    print ('bad coordinates')
                elif isinstance(e, mongoengine.errors.NotUniqueError):
                    pass
                    #print("location already loaded skipping")
                else:
                    print(e)
                    print ('invalid geojson, maybe, check error above')
                    print (feature)

    def upsert(self, request, model, json=None):
        if not json:
            #handle spaces right after the comma
            #csv.excel.skipinitialspace = True
            self.uploaded_file.open()
            fh = self.uploaded_file.file
            header = [h.strip() for h in fh.next().split(',')]
            data = csv.DictReader(self.uploaded_file,fieldnames=header, dialect=csv.excel)
            data.next() #skip header line
            mapping = self.extract_mappings(request=request, file=self.uploaded_file, model=model)
        else:
            data = json
            mapping = self.extract_mappings(request=request, model=model, json=json[0])

        obj = self.make_objects(data, mapping, model)
        # save all objects
        for o in obj:
            try:
                o.save()
            except NotUniqueError:
                # make life easy. Switch the objects and save.
                tmp = model.objects.get(name=o.name)
                o.id = tmp.id
                tmp = o
                tmp.save()

    def extract_mappings(self, request=None, file=None, model=None, json=None):
        if not all([request, model]):
            return None
        mapping = {}
        if file:
            first_row = csv.reader(file).next()
            for header in first_row:
                #a number of csv files use spaces... let's zap those
                header = header.strip()
                if not hasattr(model, request.DATA[header]):
                    print ("field not found in model", request.DATA[header])
                    #I don't think you should return None here cause that will
                    #prevent you from uploading a file that has fields you want
                    #to ignore
                    #return None
                else:
                    mapping[header] = request.DATA[header]
        if json:
            keys = json.keys()
            for key in keys:
                if not hasattr(model, request.DATA[key]):
                    continue
                mapping[key] = request.DATA[key]
        return mapping

    def make_objects(self, data=None, mapping=None, model=None):
        if not all([data, mapping, model]):
            return None
        obj_list = []
        for item in data:
            tmp = model()
            if not set(mapping.keys()) <= set(item.keys()):
                print("failed keys assumption")
                continue
            for key in mapping.keys():
                if item[key]:
                    #handle relationships like location type from location
                    attr = getattr(model, mapping[key])
                    if isinstance(attr, ReferenceField): 
                        #if we have a mongo reference field
                        #lookup reference by name
                        ref_model = attr.document_type
                        rel_obj = ref_model.objects.filter(name__iexact=str(item[key].strip()))
                        if rel_obj:
                            setattr(tmp, mapping[key], rel_obj[0])
                        else:
                            print "%s related object: %s not found" % (ref_model, item[key])
                            print "line is %s" % item

                    elif isinstance(attr, BooleanField):
                        #for boolean, follow pythonic boolean values
                        falsy = ['false', '0', 'no', 'none', 'not', 'nil', '']
                        val = str(item[key]).strip().lower()
                        setattr(tmp, mapping[key], not val in falsy)

                    elif isinstance(attr, DateTimeField):
                        #for datetime, guess the format, assume US style day first
                        val = str(item[key]).strip().lower()
                        date_val = dateparser.parse(val, dayfirst=False)
                        setattr(tmp, mapping[key], date_val)

                    else:
                        #default field type, just assume string fields
                        setattr(tmp, mapping[key], str(item[key]).strip())

            #print("adding item", tmp)
            obj_list.append(tmp)
        return obj_list


def make_normalization_entry(item, data_dict):
    '''
    item is expected to be a 2-tuple of (key, value)
    returns a dictionary entry for a dict-comprehension
    '''
    return {"norm_field" : item[1],
             "datatype" : data_dict.get(item[0] + "_datatype")}


def build_normalization_dict(data_dict):
    '''
    takes the list of parameters... i.e. request.POST
    converts them to a more useful data structure for normalization
    '''
    excl = ['csrfmiddlewaretoken']
    return  { f[0] : make_normalization_entry(f, data_dict) 
              for f in data_dict.iteritems() 
              if (f[0] not in excl and not f[0].endswith("datatype"))}

def should_normalize(norm_data):
    '''
    if we have a text datatype and no norm_field mapping then no need to
    normalize
    '''
    text_datatype = norm_data['datatype'].lower() == 'text'
    has_norm_field = norm_data['norm_field'] != ''

    return has_norm_field or not text_datatype

@api_view(['POST',])
@renderer_classes((renderers.TemplateHTMLRenderer,renderers.JSONRenderer,))
def normalize(request, import_id):
    data = init_data()
    data['errors']= {'msg': []} 
    norm_data = {} 
    try:
        if request.method == 'POST':
            data_set = Data.objects.filter(import_id=import_id)
            norm_data = build_normalization_dict(request.POST)
            for norm in norm_data.iteritems():
                if should_normalize(norm[1]):
                    datatype = norm[1]["datatype"].lower()
                    datatype_not_text = (datatype != "text")

                    norm_field = norm[1]["norm_field"]
                    has_norm_field = (norm_field != "")
                    orig_field_name = norm[0]
                        
                    for d in data_set:
                        if orig_field_name in d:
                            if datatype_not_text:
                                val = d[orig_field_name]
                                new_val = val
                                #covert to proper type skip empty values
                                if isinstance(val, basestring):
                                    val = val.strip()
                                if val == "":
                                    continue
                                try:
                                    if datatype == "number":
                                        #throw away decimal numbers
                                        val = str(val).replace(",", "")
                                        new_val = int(float(val))
                                    elif datatype == "decimal":
                                        val = str(val).replace(",", "")
                                        new_val = float(val)
                                    elif datatype == "date":
                                        new_val = dateparser.parse(val, dayfirst=False)
                                    elif datatype == "boolean":
                                        new_val = bool(val)
                                    setattr(d, orig_field_name, new_val)
                                except:
                                    #limit to 10 errors
                                    if len(data['errors']['msg']) < 10:
                                        data['errors']['msg'].append("Error converting value %s from field %s to %s" %
                                                          (val, orig_field_name,datatype)) 
                                    else:
                                        data['errors']['msg'].append("Max errors reached. Please correct errors and try again")
                                        raise StopIteration()
                            if has_norm_field:
                                setattr(d, norm_field, getattr(d, orig_field_name))
                                #delattr(d, orig_field_name)
                                #d._dynamic_fields[norm_field] = org_field
                                delattr(d, orig_field_name)
                            d.save()
    except StopIteration:
        pass

    if not data['errors']['msg']:
        # make sure we have the correct redirect url
        redir_url = "/maps-admin/settings-importfile"
        redir_url += "?id=%s" % (import_id)
        redir_url += "&step=conversion"
        return redirect(redir_url)
    else:
        data['step'] = 'normalize'
        #just need the object id
        data['object'] = DataImport.objects.get(id=import_id)
        data['normalized_fields'] = DATA_NORMALIZATION_FIELDS
        data['fields'] = [x for x in norm_data.iterkeys()]

        return Response(data=data, template_name=template_base_path + 'settings-importfile.html')



def conversion(request, import_id):
    if request.method == 'POST':
        fields = request.POST.getlist('fields[]', None)
        conversion_type = request.POST.getlist('type[]', None)
        from_unit = request.POST.getlist('from[]', None)
        to_unit = request.POST.getlist('to[]', None)
        if fields and conversion_type and len(fields) == len(conversion_type):
            data_set = Data.objects.filter(import_id=import_id)
            for i in range(len(fields)):
                fld = fields[i]
                for d in data_set:
                    if hasattr(d, fld):
                        original = getattr(d, fld)
                        converted = convert(
                            original, conversion_type[i], (from_unit[i], to_unit[i]))
                        setattr(d, fld, converted)
                        d.save()

    return redirect(request.META['HTTP_REFERER'].replace("conversion","table"))
