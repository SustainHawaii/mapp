import mongoengine as mongo
from datetime import datetime
import maps.locations as loc
from maps.data_import.models import DataImport


class Categories(mongo.Document):
    id = mongo.UUIDField(required=False)
    name = mongo.StringField(required=True, default='', unique=True)
    privacy = mongo.StringField(required=True, default='')
    description = mongo.StringField(required=True, default='')
    taxonomies = mongo.StringField(required=False, default='')
    custom_field_form = mongo.ReferenceField("FormSchema", required=False)
    created = mongo.StringField(required=True, default=str(datetime.now()))
    created_by = mongo.StringField(required=False)
    updated = mongo.StringField(required=True, default=str(datetime.now()))
    tagged = mongo.ListField(mongo.GenericReferenceField(), required=False)

    meta = {
        'indexes': [{'fields': ('name',), 'unique': True}]
    }

    def add_object(self, obj):
        self.tagged.append(obj)
        self.save()

    @property
    def group(self):
        return "Categories"

    @property
    def permission_type(self):
        return "category"

    @property
    def number_using(self):
        return len(self.tagged)

    @classmethod
    def objects_with(cls,name):
        try:
            return Categories.objects.get(name=name).tagged
        except Categories.DoesNotExist:
            return []

    @classmethod
    def for_object(cls,obj):
        return Categories.objects(tagged__in=[obj])

    @classmethod
    def for_object_id(cls,objid, cls_name):

        #kinda an ugly hack, but global should have most everything loaded
        #if your getting a Keyerror, try importing the cls
        cls = globals()[cls_name]
        obj = cls.objects.get(id=objid)
        return Categories.for_object(obj)


    @classmethod
    def remove_obj(cls, obj):
        for cat in Categories.for_object(obj):
            Categories.objects(id=str(cat.id)).update_one(pull__tagged=obj)

class Taxonomy(mongo.Document):
    id = mongo.UUIDField(required=False)
    name = mongo.StringField(required=True, default='', unique=True)
    privacy = mongo.StringField(required=True, default='')
    description = mongo.StringField(required=True, default='')
    inherit = mongo.ReferenceField('self', required=False)
    model = mongo.StringField(required=False, default='')
    compare = mongo.StringField(required=False, default='')
    model_id = mongo.StringField(required=False)
    custom_field_form = mongo.ReferenceField("FormSchema", required=False)
    created = mongo.StringField(required=True, default=str(datetime.now()))
    updated = mongo.StringField(required=True, default=str(datetime.now()))
    created_by = mongo.StringField(required=False)

    @property
    def group(self):
        return "Taxonomy"

    @property
    def number_using(self):
        count = [l for l in loc.models.LocationType.objects() if self in l.taxonomies]
        return len(count)
