# -*- coding: utf-8 -*-
import json
import os
from maps.users.models import UserTypes, User
from mongoengine.queryset import DoesNotExist


def create_fixtures():
    """
        Insert fixtures
    """
    user_type_fixtures()


def user_type_fixtures():
    pwd = os.path.dirname(os.path.realpath(__file__))
    obj = json.load(open(pwd + '/users.usertypes.json'))

    for i in obj:
        UserTypes.objects.get_or_create(**i)
    [u.delete() for u in User.objects]

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
    lh_type = UserTypes.objects.get(name='Landholder')
    try:
        landholder = User.objects.get(email="test.landholder@sh.com")
    except DoesNotExist:
        landholder = User(
            full_name='landholder', email='test.landholder@sh.com',
            password='', user_types=[lh_type],
            address='', city='', zip='', state='', description='')
        landholder.set_password('test')
        landholder.save()
    pr_type = UserTypes.objects.get(name='Provider')
    try:
        provider = User.objects.get(email="test.provider@sh.com")
    except DoesNotExist:
        provider = User(
            full_name='provider', email='test.provider@sh.com',
            password='', user_types=[pr_type],
            address='', city='', zip='', state='', description='')
        provider.set_password('test')
        provider.save()
    try:
        provider = User.objects.get(email="test.provider1@sh.com")
    except DoesNotExist:
        provider = User(
            full_name='provider1', email='test.provider1@sh.com',
            password='', user_types=[pr_type],
            address='', city='', zip='', state='', description='')
        provider.set_password('test')
        provider.save()
    try:
        provider = User.objects.get(email="test.provider2@sh.com")
    except DoesNotExist:
        provider = User(
            full_name='provider2', email='test.provider2@sh.com',
            password='', user_types=[pr_type],
            address='', city='', zip='', state='', description='')
        provider.set_password('test')
        provider.save()
    gr_type = UserTypes.objects.get(name='Grower')
    try:
        grower = User.objects.get(email="test.grower@sh.com")
    except DoesNotExist:
        grower = User(
            full_name='grower', email='test.grower@sh.com',
            password='', user_types=[gr_type],
            address='', city='', zip='', state='', description='')
        grower.set_password('test')
        grower.save()
