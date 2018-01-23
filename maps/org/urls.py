from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
import json_views

adminurls = patterns(
    '',
    url(r'^org-add$', 'maps.org.views.org_add_view'),
    url(r'^org-update/(?P<id>[\w]{24})/$', 'maps.org.views.org_update_view', name='org-update'),
    url(r'^org-delete/(?P<id>[\w]{24})/$', 'maps.org.views.org_delete_view'),
)


jsonurls = patterns(
    '',
    url(r'^org/$', json_views.AddOrganization.as_view()),
    url(r'^org/(?P<id>[\w]{24})/$', json_views.UpdateOrganization.as_view()),
)

jsonurls = format_suffix_patterns(jsonurls)
