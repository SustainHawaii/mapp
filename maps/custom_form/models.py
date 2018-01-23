import datetime
import mongoengine as mongo


class FormSchema(mongo.Document):
    id = mongo.UUIDField(required=False)
    field_groups = mongo.DynamicField(required=False)
    created = mongo.DateTimeField(default=datetime.datetime.today().date(), required=False)
    last_updated = mongo.DateTimeField(default=datetime.datetime.today().date(), required=False)

    @property
    def permission_type(self):
        return "forms"


    def convert_to_json(self):
        return {
            'id': str(self.id),
            'field_groups': self.field_groups,
            'created': self.created,
            'last_updated': self.last_updated
        }


class FormData(mongo.Document):
    id = mongo.UUIDField(required=False)
    location = mongo.ReferenceField("Location", required=False)
    user = mongo.ReferenceField("User", required=False)
    form_schema = mongo.DynamicField(required=False)
    data = mongo.DynamicField(required=False)
    created = mongo.DateTimeField(default=datetime.datetime.today().date(), required=False)
    last_updated = mongo.DateTimeField(default=datetime.datetime.today().date(), required=False)
