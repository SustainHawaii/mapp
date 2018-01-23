import mongoengine as mongo


class Data(mongo.DynamicDocument):
    import_id = mongo.StringField(required=True)


class DataImport(mongo.Document):
    id = mongo.UUIDField(required=False)
    upload_type = mongo.StringField(required=True)
    upload_format = mongo.StringField(required=True)
    duplicate_content = mongo.StringField(required=True)
    description = mongo.StringField(required=False)
    content_status = mongo.StringField(required=False)
    content_author = mongo.StringField(required=False)

    upload_file = mongo.StringField(required=False)
    upload_url = mongo.URLField(required=False)
    upload_freq = mongo.IntField(required=False)

    last_updated = mongo.DateTimeField(required=True)
    fields = mongo.ListField(required=False)
    name = mongo.StringField(required=True)

    meta = {'allow_inheritance': True}

    @property
    def datatype(self):
        dt = {"0": "csv",
              "1": "json",
              "2": "shapefile",
              "3": "geojson",
              }
        return dt.get(self.upload_format, "unknown")

    @property
    def group(self):
        if self.upload_type == "0":
            return "Imported from File"
        else:
            return "Imported from Live Feed"
