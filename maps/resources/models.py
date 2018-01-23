import mongoengine as mongo
from maps.data_visualization.models import DataVisualization
from django.conf import settings
from maps.locations.models import LocationType


class Resources(mongo.Document):
    name = mongo.StringField(required=False, unique=True)

    # Resource limited to which usertypes?
    privacy = mongo.StringField(required=False, default="private", choices=['private', 'everyone'])
    description = mongo.StringField(required=False, max_length=255)
    page_background = mongo.StringField(required=False)
    page_logo = mongo.StringField(required=False)
    color_scheme = mongo.StringField(required=False)
    display_map = mongo.BooleanField(required=False, default=True)
    content_status = mongo.StringField(required=False, default='draft', choices=['draft', 'published'])

    # Simple, flat representation. [{id:XXX, type:XXX, name:XXX}...n]
    layout = mongo.ListField(required=False)
    main_map = mongo.ReferenceField(DataVisualization, required=False)

    @property
    def page_background_url(self):
        url = None
        if self.page_background and self.name:
            url = settings.MEDIA_URL + "resources/" + self.name + '-' + self.page_background
        return url

    @property
    def page_logo_url(self):
        url = None
        if self.page_logo and self.name:
            url = settings.MEDIA_URL + "resources/" + self.name + '-' + self.page_logo
        return url


class Settings(mongo.Document):

    enable_visualizations = mongo.BooleanField(required=False, default=True)
    enable_map_visualizations = mongo.BooleanField(required=False, default=True)
    enable_drawing_tools = mongo.BooleanField(required=False, default=True)
    enable_datatypes = mongo.BooleanField(required=False, default=True)
    enabled_location_types = mongo.ListField(mongo.StringField(max_length='20'), required=False, default=[t.name for t in LocationType.objects])
    chart_types = mongo.ListField(mongo.StringField(max_length='20'), required=False, default=['chart', 'map', 'table'])
