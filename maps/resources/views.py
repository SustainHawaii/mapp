from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import TemplateView

from .models import Resources, Settings
from maps.locations.models import LocationType
from maps.users.models import UserTypes

role = 'maps-admin'
template_base_path = 'maps-admin/resources/'


def init_data():
    return {
        'role': role,
        'app': 'resources',
    }


def fe_resources(request):
    data = {}
    return render_to_response(template_base_path + "frontend.html", data, context_instance=RequestContext(request))


@login_required(login_url='/')
def all_resources(request):
    data = init_data()
    data['data_sets'] = Resources.objects.all()

    return render_to_response(template_base_path + 'all_resources.html', data, context_instance=RequestContext(request))


@login_required(login_url='/')
def add_resources(request, id=None):
    data = init_data()
    data['location_types'] = [l.to_json() for l in LocationType.objects]
    if id:
        data['id'] = Resources.objects.get(id=id).id
    return render_to_response(template_base_path + 'add_resources.html', data, context_instance=RequestContext(request))


@login_required(login_url='/')
def fs_resources(request, id):
    data = init_data()
    if id:
        data['id'] = Resources.objects.get(id=id).id
    return render_to_response(template_base_path + 'fs_resources.html', data, context_instance=RequestContext(request))


@login_required(login_url='/')
def resources_settings(request):
    data = init_data()
    data['chart_types'] = ['chart', 'table', 'map']
    # data['d_tools'] = ['none', 'circle', 'rect', 'polygon', 'freedraw', 'print', 'share']
    if len(Settings.objects):
        data['settings'] = Settings.objects[0].id
    else:
        settings = Settings()
        settings.save()
        data['settings'] = Settings.objects[0].id
    return render_to_response(template_base_path + 'resources_settings.html', data, context_instance=RequestContext(request))


class Partial(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        template_name = kwargs['template_name']

        if template_name.endswith("/"):
            template_name = template_name[:-1]
        self.template_name = 'maps-admin/resources/partials/%s.html' % (
            template_name)
        return super(Partial, self).dispatch(request, *args, **kwargs)
