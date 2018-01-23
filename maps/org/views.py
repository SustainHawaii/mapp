from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from maps.core import api
import requests
role = 'maps-admin'


def org_add_view(request):
    return render_to_response('maps-admin/users/users-addorg.html',
                              {'role': role},
                              context_instance=RequestContext(request))


def org_update_view(request, id):

    template = 'maps-admin/users/users-addorg.html'
    return render_to_response(template, {
        'role': role,
        'object': api.org.get(id=id),
    }, context_instance=RequestContext(request))


def org_delete_view(request, id):
    requests.delete(settings.CORE_API_URL + '/org/' + id)
    next = request.GET.get('next', None)
    if next:
        url = next
    else:
        url = '/maps-admin/users'

    return redirect(url)
