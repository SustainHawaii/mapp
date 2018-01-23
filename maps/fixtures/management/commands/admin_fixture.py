# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from maps.fixtures.users.admin_script import create_fixtures


def load_data():
    create_fixtures()

class Command(BaseCommand):
    help = 'Create default fixtures into database.'

    def handle(self, *args, **options):
        """
            Insert fixtures
        """
        load_data()
        
