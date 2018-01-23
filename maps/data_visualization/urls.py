from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import patterns, url
from maps.data_visualization.views import Partial
from maps.data_visualization import api_view

urlpatterns = patterns(
    '',
    url(r'visualizations$', 'maps.data_visualization.views.datavisualization_view'),
    url(r'addvisualization$', 'maps.data_visualization.views.data_add_visualization_view'),
    url(r'update-visualization/(?P<id>[\w]{24})/$', 'maps.data_visualization.views.update_data_visualization_view'),
    url(r'^dataviz-delete/(?P<id>[\w]{24})/$', 'maps.data_visualization.views.delete_view'),
    url(r'datasubtypes$', 'maps.data_visualization.views.data_subtype_view'),
    url(r'settings$', 'maps.data_visualization.views.data_settings_view'),
    url(r'dataconversions$', 'maps.data_visualization.views.data_conversion_view'),
    url(r'get-map/(?P<id>[\w]{24})/$', 'maps.data_visualization.views.get_map'),
    url(r'partials/(?P<template_name>[-_\w]+/$)', Partial.as_view()),
    url(r'show-viz/(?P<id>[\w]{24})/$', 'maps.data_visualization.views.show_viz'),
    url(r'share-viz/(?P<id>[\w]{24})/$', 'maps.data_visualization.views.share_viz'),
)

jsonurls = patterns('',
    url(r'dataviz/$', api_view.AddDataViz.as_view(), name="Add-DataViz"),
    url(r'dataviz/(?P<id>[\w]{24})/$', api_view.UpdateDataViz.as_view(), name="Update-DataViz"),
    url(r'dataviz/shorturl/(?P<id>[\w]{24})/$', api_view.shortUrl),
)
jsonurls = format_suffix_patterns(jsonurls)

