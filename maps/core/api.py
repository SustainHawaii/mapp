from maps.core import Requester
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


locations = Requester("location")
locationtypes = Requester("locationtype")
org = Requester("org")
tags = Requester("categories")
taxonomy = Requester("taxonomy")
taxonomy_tags = Requester("taxonomy-tags")
usertypes = Requester("usertypes")
dataviz = Requester("dataviz")
users = Requester("users")
