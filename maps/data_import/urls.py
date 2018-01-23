from rest_framework.urlpatterns import format_suffix_patterns

from django.conf.urls import patterns, url
import views
import admin_view

urlpatterns = patterns(
    '',
    url(r'^$', views.AddDataImport.as_view(), name='add-data-import'),
    url(r'^(?P<id>[\w]{24})/$', views.UpdateDataImport.as_view(), name='update-data-import'),
    url(r'^normalize/(?P<import_id>[\w]{24})$', admin_view.normalize, name='normalize-data'),
    url(r'^conversion/(?P<import_id>[\w]{24})$', admin_view.conversion, name='convert-data'),
    url(r'^get-data/(?P<import_id>[\w]{24})$', views.RetrieveData.as_view()),
    url(r'^get-data/$', views.BulkRetrieveData.as_view()),
    url(r'^get-data/geo/$', views.BulkRetrieveGeoJson.as_view()),
    url(r'^datatable/(?P<import_id>[\w]{24})$', views.datatable, name='data-datatable'),

    url(r'^get-fields$', admin_view.get_fields),
)

urlpatterns = format_suffix_patterns(urlpatterns)
