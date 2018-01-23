from datetime import datetime
import mongoengine as mongo
from maps.data_import.models import DataImport


class Widget(mongo.EmbeddedDocument):
    chart_options = mongo.DictField(required=False)
    config_fields = mongo.DictField(required=False)
    title = mongo.StringField(required=False)
    viz_type = mongo.StringField(required=True)
    chart_type = mongo.StringField(required=False)
    data_fields = mongo.ListField(required=False)
    viz_datasets = mongo.ListField(mongo.DictField(),
                                   required=False)
    show = mongo.BooleanField(default=False)
    raw_data = mongo.DictField(required=False)
    chart_data = mongo.ListField(required=False)


class DataSet(mongo.EmbeddedDocument):
    id = mongo.StringField(required=True)
    name = mongo.StringField(required=True)
    group = mongo.StringField(required=True)
    description = mongo.StringField(required=False)


class DataVisualization(mongo.Document):
    id = mongo.UUIDField(required=False)
    group_name = mongo.StringField(required=True, unique=True)
    selected_external_ds = mongo.ListField(mongo.EmbeddedDocumentField(DataSet),
                                           required=False)
    selected_internal_ds = mongo.ListField(mongo.EmbeddedDocumentField(DataSet),
                                           required=False)
    widgets = mongo.ListField(mongo.EmbeddedDocumentField(Widget))
    created = mongo.DateTimeField(required=False, default=datetime.now())
    updated = mongo.DateTimeField(required=False, default=datetime.now())
    short_url = mongo.StringField(required=False)
    hidden = mongo.BooleanField(default=False)

    @property
    def num_datasets(self):
        return len(self.selected_external_ds) + len(self.selected_internal_ds)

    @property
    def visualization_types(self):
        return list(set([w.viz_type for w in self.widgets]))

    @property
    def visualizations(self):
        return len(self.widgets)
