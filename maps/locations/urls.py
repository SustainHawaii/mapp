from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from maps.locations import json_views

adminurls = patterns(
    '',
    url(r'^locations$', 'maps.locations.views.locations_view'),
    url(r'^locations-addlocation$', 'maps.locations.views.locations_add_view', name='location-add'),
    url(r'^locations-update/(?P<id>[\w]{24})/$', 'maps.locations.views.locations_update_view', name='location-update'),
    url(r'^locations-delete/(?P<id>[\w]{24})/$', 'maps.locations.views.locations_delete_view'),

    url(r'^locations-types$', 'maps.locations.views.locations_type_view'),
    url(r'^locations-addlocationtype$', 'maps.locations.views.locations_add_type_view'),
    url(r'^locationtype-update/(?P<id>[\w]{24})/$', 'maps.locations.views.locations_type_update_view'),
    url(r'^locationtype-delete/(?P<id>[\w]{24})/$', 'maps.locations.views.locations_type_delete_view'),
)


jsonurls = patterns(
    '',
    url(r'^location/$', json_views.AddLocation.as_view(), name="Add-Location"),
    url(r'^location/(?P<id>[\w]{24})/$', json_views.UpdateLocation.as_view(),name="Update-Location"),
    url(r'^location/(?P<location_id>[\w]{24})/form/$', json_views.SaveLocationFormData.as_view(), name="Save-Location-Form-Data"),
    url(r'^location/form-data/(?P<location_id>[\w]{24})?', json_views.LocationFormData.as_view(), name="Location-Form-Data"),
    url(r'^location/search/$', json_views.MapSearch.as_view()),
    url(r'^location/geo/$', json_views.get_map_points),
    url(r'^location/geo/(?P<id>[\w]{24})/$$', json_views.get_map_point),

    url(r'^locationtype/$', json_views.AddLocationType.as_view(), name="Add-Location-Type"),
    url(r'^locationtype/(?P<id>[\w]{24})/$', json_views.UpdateLocationType.as_view(), name="Update-Location-Type"),
    url(r'^locationtype/form-data/(?P<location_id>[\w]{24})?', json_views.LocationTypeFormData.as_view(), name="Location-Type-Form-Data"),

    url(r'^location/datatable', json_views.locations_datatable, name='location-datatable'),
)

jsonurls = format_suffix_patterns(jsonurls)
