from django.contrib.auth.decorators import login_required
import json
import random_data
from django.shortcuts import render_to_response
from django.template import RequestContext
from mongoengine.queryset import Q
from pygeocoder import Geocoder
from maps.users.models import User
from maps.locations.models import Location
from maps.org.models import Organization


def init_data(request):
    data = {
        'role': request.user.current_role,
        'data': random_data.random()
    }
    if request.user.is_authenticated():
        data['mapp_user'] = User.objects.get(id=request.user.id)

    return data


@login_required(login_url='/')
def dashboard_view(request):
    return render_to_response('maps-admin/dashboard/dashboard.html', init_data(request),
                              context_instance=RequestContext(request))


# Forms Directory
@login_required(login_url='/')
def forms_view(request):
    return render_to_response('maps-admin/forms/forms.html', init_data(request),
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def forms_add_view(request):
    return render_to_response('maps-admin/forms/forms-addform.html', init_data(request),
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def forms_settings_view(request):
    return render_to_response('maps-admin/forms/forms-settings.html', init_data(request),
                              context_instance=RequestContext(request))


# Profile Directory
@login_required(login_url='/')
def profile_view(request):
    return render_to_response('maps-admin/profile/profile.html', init_data(request),
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def profile_myentities_view(request):
    data = init_data(request)
    data['org'] = Organization.objects.filter(created_by__contains=str(request.user.id))

    return render_to_response('maps-admin/profile/profile-myentities.html', data,
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def profile_mylocations_view(request):
    data = init_data(request)
    data['locations'] = Location.objects.filter(Q(created_by__contains=str(request.user.id)) |
                                                Q(also_editable_by__contains=str(request.user.id)))

    return render_to_response('maps-admin/profile/profile-mylocations.html', data,
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def settings_view(request):
    return render_to_response('maps-admin/settings/settings.html', init_data(request),
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def settings_menus_view(request):
    return render_to_response('maps-admin/settings/settings-menus.html', init_data(request),
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def settings_plugins_view(request):
    return render_to_response('maps-admin/settings/settings-plugins.html', init_data(request),
                              context_instance=RequestContext(request))


def verify_address(data):
    try:
        results = Geocoder.geocode(data)
        if results[0].coordinates:
            lat = results[0].coordinates[0]
            log = results[0].coordinates[1]
            return json.dumps({'latitude': lat, 'longitude': log})
    except ValueError:
        return json.dumps({'Error': "Invalid Address"})
