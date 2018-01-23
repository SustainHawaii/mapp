from maps.users import api_view
from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns(
    '',
    url(r'^$', 'maps.users.views.users', name='user-list'),
    url(r'^add-user$', 'maps.users.views.user_add'),
    url(r'^update-user/(?P<user_id>[\w]{24})/$', 'maps.users.views.user_update'),

    url(r'^user-types/$', 'maps.users.views.user_types'),
    url(r'^add-usertype/$', 'maps.users.views.user_type_add'),
    url(r'^update-usertypes/(?P<user_type_id>[\w]{24})/$', 'maps.users.views.user_type_update'),
)

users_json_urls = patterns(
    '',
    url(r'^users/$', api_view.AddUser.as_view()),
    url(r'^users/(?P<id>[\w]{24})/$', api_view.UpdateUser.as_view()),
    url(r'^users/(?P<obj_id>[\w]{24})/form/$', api_view.SaveUserFormData.as_view(), name="Save-User-Form-Data"),
    url(r'^users/form-data/(?P<obj_id>[\w]{24})?', api_view.UserFormData.as_view(), name="User-Form-Data"),

    url(r'^users/profile/(?P<id>[\w]{24})/$', api_view.UpdateUserProfile.as_view()),
    url(r'^usertypes/$', api_view.UserTypesAPI.ListView.as_view()),
    url(r'^usertypes/(?P<id>[\w]{24})/$', api_view.UserTypesAPI.ItemView.as_view()),
    url(r'^usertypes/form-data?', api_view.UserTypeFormData.as_view()),
    url(r'^usertypes/form-data/(?P<usertype_id>[\w]{24})?', api_view.UserTypeFormData.as_view()),
)

users_json_urls = format_suffix_patterns(users_json_urls)
