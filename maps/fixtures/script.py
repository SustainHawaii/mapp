from maps.locations.models import LocationType, Location
from maps.locations.json_views import verify_address
from django.conf import settings
from maps.data_import.models import Data, DataImport
from maps.data_import.admin_view import parse_csv
from maps.data_import.serializers import DataImportSerializer
import os
import datetime
import shutil


def move_files():
    location_path = os.path.join(
        settings.BASE_DIR, 'maps/fixtures', 'location_type')
    import_path = os.path.join(settings.BASE_DIR, 'maps/fixtures', 'data_import')

    if os.path.exists(os.path.join(settings.MEDIA_ROOT, "location_type")):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, "location_type"))

    if os.path.exists(os.path.join(settings.MEDIA_ROOT, "data_import")):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, "data_import"))

    shutil.copytree(
        location_path, os.path.join(settings.MEDIA_ROOT, "location_type"))
    shutil.copytree(
        import_path, os.path.join(settings.MEDIA_ROOT, "data_import"))


def create_location_type():

    # Create state location type
    location_type, created = LocationType.objects.get_or_create(
        name="state",
    )
    if created:
        location_type.save()

    # Create county location type
    location_type, created = LocationType.objects.get_or_create(
        name="county",
    )
    if created:
        location_type.save()

    # Create island location type
    location_type, created = LocationType.objects.get_or_create(
        name="island",
    )
    if created:
        location_type.save()

    # Create community location type
    location_type, created = LocationType.objects.get_or_create(
        name="community",
    )
    if created:
        location_type.save()

    # Create district location type
    location_type, created = LocationType.objects.get_or_create(
        name="district",
    )
    if created:
        location_type.save()

    # Create precint location type
    location_type, created = LocationType.objects.get_or_create(
        name="precint",
    )
    if created:
        location_type.save()

    # Create ahupua'a location type
    location_type, created = LocationType.objects.get_or_create(
        name="ahupuaa",
    )
    if created:
        location_type.save()

    # Create TMK location type
    location_type, created = LocationType.objects.get_or_create(
        name="TMK",
    )
    if created:
        location_type.save()        


def create_location_type_iconed():

    # Create wholesalers location type
    location_type, created = LocationType.objects.get_or_create(
        name="wholesalers",
    )
    if created:
        location_type.icon = ("location_type/wholesalers.png")
        location_type.save()

    # Create retailers location type
    location_type, created = LocationType.objects.get_or_create(
        name="retailers",
    )
    if created:
        location_type.icon = ("location_type/retailers.png")
        location_type.save()

    # Create farmers location type
    location_type, created = LocationType.objects.get_or_create(
        name="farmers",
    )
    if created:
        location_type.icon = ("location_type/farmers.png")
        location_type.save()

    # Create restauranteurs location type
    location_type, created = LocationType.objects.get_or_create(
        name="restauranteurs",
    )
    if created:
        location_type.icon = ("location_type/restauranteurs.png")
        location_type.save()

    # Create homes location type
    location_type, created = LocationType.objects.get_or_create(
        name="homes",
    )
    if created:
        location_type.icon = ("location_type/homes.png")
        location_type.save()

    # Create processors location type
    location_type, created = LocationType.objects.get_or_create(
        name="processors",
    )
    if created:
        location_type.icon = ("location_type/processors.png")
        location_type.save()


def create_location():
    # Create wholesalers location
    location, created = Location.objects.get_or_create(
        name="Wholesalers",
    )
    if created:
        location.address1 = "Hawaii Business 1000 Bishop St., Ste. 405"
        location.city = "Honolulu"
        location.state = "HI"
        location.zip = "96813"
        location.phone = "09"
        location.description = "say something"
        location.location_type = LocationType.objects.get(name="wholesalers")
        location.org_name = "Whole Salers Union"
        location.org_address1 = "Hawaii Business 1000 Bishop St., Ste. 405"
        location.org_city = "Honolulu"
        location.org_country = "USA"
        location.org_phone = "09"
        location.org_state = "HI"
        location. org_website = "http://www.hawaii.com"
        location.point = verify_address(
            location.address1 + "," + location.zip + "," + location.city + "," + location.state)
        location.save()

    # Create retailers location
    location, created = Location.objects.get_or_create(
        name="retailers",
    )
    if created:
        location.address1 = "5535 Kalanianaole Highway"
        location.city = "Honolulu"
        location.state = "HI"
        location.zip = "96821"
        location.phone = "09"
        location.description = "say something"
        location.location_type = LocationType.objects.get(name="retailers")
        location.org_name = "Retailers Union"
        location.org_address1 = "5535 Kalanianaole Highway"
        location.org_city = "Honolulu"
        location.org_country = "USA"
        location.org_phone = "09"
        location.org_state = "HI"
        location. org_website = "http://www.hawaii.com"
        location.point = verify_address(
            location.address1 + "," + location.zip + "," + location.city + "," + location.state)
        location.save()

    # Create farmers location
    location, created = Location.objects.get_or_create(
        name="farmers",
    )
    if created:
        location.address1 = "Papaikou"
        location.city = "Honolulu"
        location.state = "HI"
        location.zip = "96781"
        location.phone = "09"
        location.description = "say something"
        location.location_type = LocationType.objects.get(name="farmers")
        location.org_name = "Vetiver Farms Hawaii"
        location.org_address1 = "Papaikou"
        location.org_city = "Honolulu"
        location.org_country = "USA"
        location.org_phone = "09"
        location.org_state = "HI"
        location. org_website = "http://www.hawaii.com"
        location.point = verify_address(
            location.address1 + "," + location.zip + "," + location.city + "," + location.state)
        location.save()

        # Create restauranteurs location
    location, created = Location.objects.get_or_create(
        name="restauranteurs",
    )
    if created:
        location.address1 = "6600 Kalanianaole Hwy"
        location.city = "Honolulu"
        location.state = "HI"
        location.zip = "96825"
        location.phone = "09"
        location.description = "say something"
        location.location_type = LocationType.objects.get(
            name="restauranteurs")
        location.org_name = "The Original Roy in Hawaii Kai"
        location.org_address1 = "6600 Kalanianaole Hwy"
        location.org_city = "Honolulu"
        location.org_country = "USA"
        location.org_phone = "09"
        location.org_state = "HI"
        location. org_website = "http://www.hawaii.com"
        location.point = verify_address(
            location.address1 + "," + location.zip + "," + location.city + "," + location.state)
        location.save()

        # Create homes location
    location, created = Location.objects.get_or_create(
        name="homes",
    )
    if created:
        location.address1 = "6600 Kalanianaole Hwy"
        location.city = "Honolulu"
        location.state = "HI"
        location.zip = "96825"
        location.phone = "09"
        location.description = "say something"
        location.location_type = LocationType.objects.get(name="homes")
        location.org_name = "help home"
        location.org_address1 = "6600 Kalanianaole Hwy"
        location.org_city = "Honolulu"
        location.org_country = "USA"
        location.org_phone = "09"
        location.org_state = "HI"
        location.org_website = "http://www.hawaii.com"
        location.point = verify_address(
            location.address1 + "," + location.zip + "," + location.city + "," + location.state)
        location.save()

    # Create processors location
    location, created = Location.objects.get_or_create(
        name="processors",
    )
    if created:
        location.address1 = "6600 Kalanianaole Hwy"
        location.city = "Honolulu"
        location.state = "HI"
        location.zip = "96825"
        location.phone = "09"
        location.description = "say something"
        location.location_type = LocationType.objects.get(name="processors")
        location.org_name = "Meat processors"
        location.org_address1 = "6600 Kalanianaole Hwy"
        location.org_city = "Honolulu"
        location.org_country = "USA"
        location.org_phone = "091"
        location.org_state = "HI"
        location. org_website = "http://www.hawaii.com"
    location.save()

# for i in range(110):
#         location, created = Location.objects.get_or_create(
#             name = "dummy_loc_" + str(i),
#         )
#         if created:
#             location.address1 = "5535 Kalanianaole Highway"
#             location.city = "Honolulu"
#             location.state = "HI"
#             location.zip = "96821"
#             location.phone = "09"
#             location.description = "say something"
#             location.location_type=LocationType.objects.get(name="retailers")
#             location.org_name = "Retailers Union"
#             location.org_address1 = "5535 Kalanianaole Highway"
#             location.org_city = "Honolulu"
#             location.org_country = "USA"
#             location.org_phone = "09"
#             location.org_state = "HI"
#             location. org_website = "http://www.hawaii.com"
#             location.point = verify_address(location.address1+","+location.zip+","+location.city+","+location.state)
#             location.save()


def create_data_import():
    # Create Data Import for food info
    try:
        data_import = DataImport.objects.get(name__exact="Food Info")

    except DataImport.DoesNotExist:
        data_import = DataImport(upload_type="0",
                                 upload_format="0",
                                 upload_file=os.path.join(
                                     settings.MEDIA_ROOT, "data_import/food_stats.csv"),
                                 duplicate_content="1",
                                 content_status="1",
                                 name="Food Info",
                                 last_updated=datetime.datetime.now())
        data_import.save()

        data, created = Data.objects.get_or_create(
            import_id=str(data_import.id),
        )
        if created:
            data.save()
    serializer = DataImportSerializer(data_import)
    parse_csv(open(serializer.object.upload_file, 'r+'),
              serializer.object, Data, 1, True)

    # Create Data Import for soil info
    try:
        data_import = DataImport.objects.get(name__exact="Environment Info")

    except DataImport.DoesNotExist:
        data_import = DataImport(upload_type="0",
                                 upload_format="0",
                                 upload_file=os.path.join(
                                     settings.MEDIA_ROOT, "data_import/env.csv"),
                                 duplicate_content="1",
                                 content_status="1",
                                 name="Environment Info",
                                 last_updated=datetime.datetime.now())
        data_import.save()

        data, created = Data.objects.get_or_create(
            import_id=str(data_import.id),
        )
        if created:
            data.save()
    serializer = DataImportSerializer(data_import)
    parse_csv(open(serializer.object.upload_file, 'r+'),
              serializer.object, Data, 1, True)
