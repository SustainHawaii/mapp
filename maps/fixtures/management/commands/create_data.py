from django.core.management.base import BaseCommand
from maps.fixtures.script import create_location_type, create_location_type_iconed, create_location, create_data_import, move_files


class Command(BaseCommand):
    help = "Creates arbitrary location types"

    def handle(self, *args, **options):
        """
                Create some location types
        """
        move_files()
        self.stdout.write("Successfully moved files")

        create_location_type()
        self.stdout.write("Sucessfully created location types")

        create_location_type_iconed()
        self.stdout.write("Sucessfully created location types with icons")

        create_location()
        self.stdout.write("Sucessfully created locations")

        create_data_import()
        self.stdout.write("Successfully created data imports")
