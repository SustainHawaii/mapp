from django.contrib.auth.decorators import login_required
from maps.core import api
from maps.users.models import User
import json, requests
from mappweb import settings
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from models import Location

role = 'maps-admin'
template_header = role + "/locations/"


@login_required(login_url='/')
def locations_view(request):    
    response = render_to_response(template_header + 'locations.html', {
        'role': role,
    }, context_instance=RequestContext(request))
    return response


@login_required(login_url='/')
def locations_add_view(request):
    return render_to_response(template_header + 'locations-addlocation.html', {
        'role': role,
    }, context_instance=RequestContext(request))


@login_required(login_url='/')
def locations_update_view(request, id):
    data = Location.objects.get(id=id)

    #if data['tags'] and data['tags'] != 'null':
    #    data['tags'] = ', '.join(data['tags'])
    #    data['tags'] = '[' + data['tags'] + ']'
    if request.user.is_authenticated():
        try:
            data['mapp_user'] = User.objects.get(id=request.user.id)
        except KeyError:
            data.mapp_user = User.objects.get(id=request.user.id)

    template = template_header + 'locations-addlocation.html'
    return render_to_response(template, {
        'role': role,
        'object': data,
    }, context_instance=RequestContext(request))


@login_required(login_url='/')
def locations_delete_view(request, id):
    requests.delete(settings.CORE_API_URL + '/location/' + id)
    next = request.GET.get('next', None)
    if next:
        url = next
    else:
        url = '/maps-admin/locations'

    return redirect(url)


@login_required(login_url='/')
def locations_type_view(request):
    template = 'locations/locations-locationtypes.html'
    return render_to_response(template, {
        'role': role,
        'objects': api.locationtypes.get().get('results')
    }, context_instance=RequestContext(request))


@login_required(login_url='/')
def locations_add_type_view(request):
    return render_to_response(template_header + 'locations-addlocationtype.html', {
        'role': role,
    }, context_instance=RequestContext(request))


@login_required(login_url='/')
def locations_type_update_view(request, id):
    template = template_header + 'locations-addlocationtype.html'
    return render_to_response(template, {
        'role': role,
    }, context_instance=RequestContext(request))


@login_required(login_url='/')
def locations_type_delete_view(request, id):
    requests.delete(settings.CORE_API_URL + '/locationtype/' + id)
    return redirect('/maps-admin/locations-types')
























