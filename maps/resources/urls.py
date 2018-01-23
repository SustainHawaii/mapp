from . import views
from . import api_views
from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^fe_resources$', views.fe_resources),
    url(r'^all-resources$', views.all_resources),
    url(r'^add-resources$', views.add_resources),
    url(r'^add-resources/(?P<id>[\w-]+)/$', views.add_resources),
    url(r'^fs-resources/(?P<id>[\w-]+)/$', views.fs_resources),
    url(r'^resources-settings$', views.resources_settings),
    url(r'partials/(?P<template_name>[-_\w]+/$)', views.Partial.as_view()),

)

resource_api_urlpatterns = patterns(
    '',
    url(r'^resources/$', api_views.ListCreateResources.as_view()),
    url(r'^resources/(?P<id>[\w-]+)/$', api_views.RetrieveUpdateDestroyResources.as_view()),
    url(r'^resources_settings/(?P<id>[\w-]+)/$', api_views.RetrieveUpdateSettings.as_view()),
)
