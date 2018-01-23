from django.contrib import admin
from django.conf.urls import patterns, include, url
from maps.data_import.admin_view import SettingsImportFileView, SettingsImportSystemView
from maps.categories.urls import jsonurls as cat_jsonurls
from maps.locations.urls import adminurls
from maps.locations.urls import jsonurls as location_jsonurls
from maps.org.urls import adminurls as org_adminurls
from maps.org.urls import jsonurls as org_jsonurls
from django.conf import settings
from django.conf.urls.static import static
from maps.users.urls import users_json_urls
from maps.data_visualization.urls import jsonurls as dataviz_jsonurls
from maps.users import views
from maps.resources.urls import urlpatterns as resource_urlpatterns
from maps.resources.urls import resource_api_urlpatterns
from maps.resources.views import fe_resources

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/dataimport/', include('maps.data_import.urls')),

    url(r'^maps-admin/data/', include('maps.data_visualization.urls')),

    url(r'^api/v1/', include(location_jsonurls)),
    url(r'^api/v1/', include(org_jsonurls)),
    url(r'^api/v1/', include(dataviz_jsonurls)),
    url(r'^api/v1/', include(cat_jsonurls)),
    url(r'^api/v1/', include(users_json_urls)),
    url(r'^api/v1/', include(resource_api_urlpatterns)),

    url(r'^$', fe_resources, name='homepage'),
    url(r'^access/$', 'maps.django_mapp.views.loginadmin_view'),
    url(r'^register/$', 'maps.django_mapp.views.register_view'),
    url(r'^lostpassword/$', 'maps.django_mapp.views.lostpassword_view'),
    url(r'^about/$', 'maps.django_mapp.views.about_view'),
    url(r'^directory/$', 'maps.django_mapp.views.index_directory_view'),
    url(r'^map/$', 'maps.django_mapp.views.index_view'),
    url(r'^members/$', 'maps.django_mapp.views.members_view'),
    #url(r'^visualizations/$', 'maps.django_mapp.views.visualizations_view'),
    url(r'^members-profile/(?P<id>[\w]{24})/$', 'maps.django_mapp.views.members_profile_view'),
    url(r'^members-location/(?P<id>[\w]{24})/$', 'maps.django_mapp.views.members_location_view'),

    url(r'^maps-admin/', include(adminurls)),
    url(r'^maps-admin/', include(org_adminurls)),
    url(r'^maps-admin/resources/', include(resource_urlpatterns)),

    url(r'^maps-admin/dashboard$', 'maps.django_mapp.admin_view.dashboard_view', name='index'),

    url(r'^maps-admin/categories/', include('maps.categories.urls')),

    url(r'^maps-admin/users/', include('maps.users.urls')),

    url(r'^maps-admin/forms$', 'maps.django_mapp.admin_view.forms_view'),
    url(r'^maps-admin/forms-addform$', 'maps.django_mapp.admin_view.forms_add_view'),
    url(r'^maps-admin/forms-settings$', 'maps.django_mapp.admin_view.forms_settings_view'),

    url(r'^maps-admin/profile/$', 'maps.django_mapp.admin_view.profile_view'),
    url(r'^maps-admin/profile-myentities$', 'maps.django_mapp.admin_view.profile_myentities_view'),
    url(r'^maps-admin/profile-mylocations$', 'maps.django_mapp.admin_view.profile_mylocations_view'),

    url(r'^maps-admin/settings$', 'maps.django_mapp.admin_view.settings_view'),
    url(r'^maps-admin/settings-import$', 'maps.data_import.admin_view.settings_import_view', name='import-list'),
    url(r'^maps-admin/settings-importfile$', SettingsImportFileView.as_view(), name='import-file'),
    url(r'^maps-admin/settings-importsystem$', SettingsImportSystemView.as_view(), name='import-system'),
    url(r'^maps-admin/settings-menus$', 'maps.django_mapp.admin_view.settings_menus_view'),
    url(r'^maps-admin/settings-plugins$', 'maps.django_mapp.admin_view.settings_plugins_view'),

    # Email confirmation link
    url(r'^confirm/(?P<auth_key>[0-9A-Za-z]+)/$', 'maps.users.views.register_confirm'),
    url(r'^password-recovery$', 'maps.users.views.password_recover'),
    url(r'^password-reset/(?P<auth_key>[\w]+)$', 'maps.users.views.password_reset'),

    url(r'^login$', views.login),
    url(r'^signup$', views.SignUpView.as_view()),
    url(r'^logout$', 'maps.users.views.logout_view')
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
