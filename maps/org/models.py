import datetime
import mongoengine as mongo
from maps.locations.json_views import verify_address
from maps.locations.models import Location


class Organization(mongo.Document):
    id = mongo.UUIDField(required=False)
    name = mongo.StringField(max_length=255, required=True, unique=True)
    address = mongo.StringField(max_length=255, required=False)
    city = mongo.StringField(max_length=255, required=False)
    state = mongo.StringField(max_length=255, required=False)
    zip = mongo.StringField(max_length=50, required=False)
    point = mongo.PointField(required=False)
    phone = mongo.StringField(max_length=20, required=False)
    website = mongo.StringField(required=False)
    description = mongo.StringField(required=False)

    privacy = mongo.StringField(required=True, default='')
    last_updated = mongo.DateTimeField(required=True, default=datetime.datetime.now())
    created_by = mongo.StringField(required=False)

    def save(self, *args, **kwargs):
        self.last_updated = datetime.datetime.now()

        address = (self.address + ", " + self.zip, self.city, self.state)
        geocoded_addr = verify_address(address)
        if geocoded_addr != 'Error':
            self.point = geocoded_addr

        super(Organization, self).save(*args, **kwargs)

    def location_count(self):
        return Location.objects.filter(org=str(self.id)).count()

    def location_set(self):
        return Location.objects.filter(org=str(self.id))
