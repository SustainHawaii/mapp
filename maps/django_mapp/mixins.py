from __future__ import unicode_literals
import ast
import json
import urllib
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import clone_request
from rest_framework.settings import api_settings
from django.http.request import QueryDict
from maps.locations.models import Location
from maps.categories.models import Taxonomy, Categories

import warnings


def _get_validation_exclusions(obj, pk=None, slug_field=None, lookup_field=None):
    """
    Given a model instance, and an optional pk and slug field,
    return the full list of all other field names on that model.

    For use when performing full_clean on a model instance,
    so we only clean the required fields.
    """
    include = []

    if pk:
        # Deprecated
        pk_field = obj._meta.pk
        while pk_field.rel:
            pk_field = pk_field.rel.to._meta.pk
        include.append(pk_field.name)

    if slug_field:
        # Deprecated
        include.append(slug_field)

    if lookup_field and lookup_field != 'pk':
        include.append(lookup_field)

    return [field.name for field in obj._meta.fields if field.name not in include]


def get_success_headers(self, data):
    try:
        return {'Location': data[api_settings.URL_FIELD_NAME]}
    except (TypeError, KeyError):
        return {}




def add_address(id, data):
    location = Locations.objects.get(id=id)
    location.points = dict(data)
    print('save point 1')
    location.save(force_insert=True)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        print 'MyEncoder.default() called'
        if isinstance(obj, NoIndent):
            return 'MyEncoder::NoIndent object'  # hard code string for now
        else:
            return json.JSONEncoder.default(self, obj)


class NoIndent(object):
    def __init__(self, value):
        self.value = value
