import os
from django.conf import settings
import datetime
import json
import mongoengine as mongo
from django.conf import settings
from maps.categories.models import Categories, Taxonomy
from maps.custom_form.serializers import FormSchemaIdSerializer


class Location(mongo.Document):
    id = mongo.UUIDField(required=False)
    name = mongo.StringField(max_length=255, required=True, unique=True)
    address1 = mongo.StringField(max_length=255, required=False)
    city = mongo.StringField(max_length=255, required=False)
    state = mongo.StringField(max_length=255, required=False)
    zip = mongo.StringField(max_length=50, required=False)
    description = mongo.StringField(required=False, default='')
    #tags = mongo.StringField(required=False)
    phone = mongo.StringField(max_length=20, required=False)
    polygon = mongo.PolygonField(required=False)
    point = mongo.PointField(required=False)
    custom_field_form = mongo.ReferenceField("FormSchema", required=False)
    created = mongo.DateTimeField(required=False, default=datetime.datetime.today().date())
    created_by = mongo.StringField(required=False)
    last_updated= mongo.DateTimeField(required=False, default=datetime.datetime.today().date())
    also_editable_by = mongo.StringField(required=False)

    location_type = mongo.ReferenceField("LocationType", required=False)
    image = mongo.StringField(required=False)

    @property
    def tags(self):
        cats = Categories.objects(tagged__in=[self])
        '''
        print("my cats", cats)
        ret_val = []
        for c in cats:
            ret_val.append({"name":c.name, "id":str(c.id)})
        print("ret val is ", ret_val)
        return ret_val 
        '''
        return cats

    def save(self, *args, **kwargs):
        requery = False
        if not self.point:
            requery = True
        elif self.id:
            original = Location.objects.get(pk=self.id) 
            if original.formatted_address <> self.formatted_address:
                requery = True
        if requery:
            if all([self.zip, self.city, self.state]):
                from .json_views import verify_address
                geocoded_addr = verify_address(self.formatted_address)
                if geocoded_addr != 'Error':
                    self.points = geocoded_addr
        if not self.also_editable_by:
            if self.created_by:
                self.also_editable_by = self.created_by
        return super(Location, self).save(*args, **kwargs)


    def backend_form(self):
        output = []
        try:
            for tag in json.loads(self.tags):
                obj = Categories.objects.filter(name=tag)[0]
                if obj.custom_field_form:
                    serializer = FormSchemaIdSerializer(obj.custom_field_form)
                    output.append(serializer.tax)
                data = json.loads(obj.taxonomies)
                for t in tax:
                    if tax[t]:
                        t_obj = Taxonomy.objects.filter(id=t)[0]
                        serializer = FormSchemaIdSerializer(t_obj.custom_field_form)
                        output.append(serializer.data)
        except:
            pass
        return output

    def frontend_form(self):
        output = []
        try:
            if self.custom_field_form:
                serializer = FormSchemaIdSerializer(self.custom_field_form)
                output.append(serializer.data)
        except:
            pass
        return output

    def taxonomies(self):
        output = []
        try:
            for tag in json.loads(self.tags):
                cat = Categories.objects.filter(name=tag)[0]
                tax = json.loads(cat.taxonomies)
                for t in tax:
                    if tax[t]:
                        obj = Taxonomy.objects.filter(id=t)[0]
                        output.append(obj.name)
        except:
            pass
        return output

    @property
    def permission_type(self):
        return "locations"

    @property
    def image_url(self):
        url = None
        if self.image:
            url = settings.MEDIA_URL + self.image
        return url

    @image_url.setter
    def image_url(self, value):
        self.image = value

    org = mongo.StringField(max_length=255, required=False)

    def __init__(self, points=None, *args, **kwargs):
        '''allow for settings points with the property setter from init'''

        super(self.__class__, self).__init__(*args, **kwargs)
        if points:
            self.points = points

    @property
    def points(self):
        return self.point if self.point else self.polygon

    @points.setter
    def points(self, val):
        '''Points and polygons need to be stored in seperate fields for
        validators to work correctly.  This setter will allow the user to pass
        in either a point or polygon and set it to the correct field.  Thus
        effectively preventing the user from having to care if it's a point or
        polygon
        '''
        try:
            if type(val) == str or type(val) == unicode:
                val = json.loads(val)
            Location(name="test", point=val).validate()
            self.point = val
        except mongo.ValidationError:
            try:
                Location(name="test", polygon=val).validate()
                self.polygon = val
            except mongo.ValidationError:
                raise (mongo.ValidationError("points should be a valid GeoJSON Point or Polygon"))

    @property
    def formatted_address(self):
        data = []

        # must in this sequence.
        if 'address1' in self:
            data.append(self.address1)
        if 'city' in self:
            data.append(self.city)
        if 'state' in self:
            data.append(self.state)
        if 'zip' in self:
            data.append(self.zip)
        return ' '.join(data)

    @property
    def group(self):
        return "Locations"

    @classmethod
    def import_fields(cls):
        fields = Location._fields.copy()
        fields.pop("id")
        fields.pop("custom_field_form")
        fields.pop("created")
        fields.pop("created_by")
        fields.pop("last_updated")
        return fields

    @classmethod
    def required_import_fields(cls):
        return [k for (k,v) in Location.import_fields().items() if v.required]

class LocationType(mongo.Document):
    id = mongo.UUIDField(required=False)
    name = mongo.StringField(max_length=255, required=True, unique=True)
    desc = mongo.StringField(required=False)
    icon = mongo.StringField(required=False)
    allow_media = mongo.BooleanField(default=False, required=False)
    allow_galleries = mongo.BooleanField(default=False, required=False)
    allow_forms = mongo.BooleanField(default=False, required=False)
    allow_categories = mongo.BooleanField(default=False, required=False)
    taxonomies = mongo.ListField(mongo.StringField(), required=False)
    view_privacy = mongo.StringField(required=False, default="everyone")
    custom_field_form = mongo.ReferenceField("FormSchema", required=False)
    created = mongo.DateTimeField(default=datetime.datetime.today().date(), required=False)
    created_by = mongo.StringField(required=False)
    last_updated = mongo.DateTimeField(default=datetime.datetime.today().date(), required=False)

    @property
    def icon_url(self):
        url = None
        if self.icon:
            url = settings.MEDIA_URL + self.icon
            if os.path.isfile(settings.BASE_DIR + url):
                pass
            else:
                url = None
        return url

    @property
    def location_count(self):
        try:
            return Location.objects(location_type=self.id).count()
        except mongo.ValidationError:
            return 0

    @property
    def long_description(self):
        return "%s -- Num Locations: %s" % (self.desc or " ", self.location_count)

    @property
    def group(self):
        return "Location Types"


class States(mongo.Document):
    name = mongo.StringField('State name', max_length=20, required=False)
    code = mongo.StringField('State abbreviation', max_length=10, required=False)





