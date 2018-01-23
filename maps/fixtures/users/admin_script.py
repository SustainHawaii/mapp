# -*- coding: utf-8 -*-
import json
import os
from maps.users.models import UserTypes, User
from mongoengine.queryset import DoesNotExist
from mongoengine.document import NotUniqueError


def create_fixtures():
    """
        Insert fixtures
    """
    user_type_fixtures()


def user_type_fixtures():
    pwd = os.path.dirname(os.path.realpath(__file__))
    obj = json.load(open(pwd + '/users.usertypes.json'))

    for i in obj:
        try:
            UserTypes.objects.get_or_create(**i)
        except NotUniqueError:
            # For some reason the get_or_create is not managing this...
            pass

    admin_type = UserTypes.objects.get(name='Admin')
    try:
        admin_user = User.objects.get(email="admin@sh.com")
    except DoesNotExist:
        admin_user = User(
            full_name='admin', email='admin@sh.com',
            password='', user_types=[admin_type],
            address='', city='', zip='', state='', description='')
        admin_user.set_password('test')
        admin_user.save()
