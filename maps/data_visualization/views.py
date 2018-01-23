from django.template import RequestContext
import json
import pprint
from bson import ObjectId
import datetime
from maps.data_import.models import DataImport, Data
from django.http import HttpResponse
from django.shortcuts import render_to_response
from maps.data_visualization.models import DataVisualization
from mappweb.settings import DATA_IMPORT_OPTIONS
from django.views.generic import TemplateView
import requests
from django.conf import settings
from django.shortcuts import redirect

role = 'maps-admin'


def init():
    data = {'role': role}
    return data


def delete_view(request, id):
    requests.delete(settings.CORE_API_URL + '/dataviz/' + id)
    next = request.GET.get('next', None)
    if next:
        url = next
    else:
        url = '/maps-admin/data/visualizations'

    return redirect(url)




def datavisualization_view(request):
    data = init()
    template = 'maps-admin/data/datavisualizations.html'
    try:
        data['data_sets'] = DataVisualization.objects.all()
    except:
        data['data_sets'] = []
    return render_to_response(template, data, context_instance=RequestContext(request))


def data_add_visualization_view(request):
    data = init()
    template = 'maps-admin/data/data-addvisualization.html'
    return render_to_response(template, data, context_instance=RequestContext(request))


def update_data_visualization_view(request, id):
    data = init()
    data['id'] = id
    template = 'maps-admin/data/data-addvisualization.html'
    return render_to_response(template, data, context_instance=RequestContext(request))


def show_viz(request, id):
    data = init()
    data['id'] = id
    template = 'maps-admin/data/show_viz.html'
    return render_to_response(template, data, context_instance=RequestContext(request))


def share_viz(request, id):
    data = init()
    data['id'] = id
    template = 'maps-admin/data/share_viz.html'
    return render_to_response(template, data, context_instance=RequestContext(request))


def data_conversion_view(request):
    data = init()
    template = 'maps-admin/data/data-dataconversions.html'
    return render_to_response(template, data, context_instance=RequestContext(request))


def data_subtype_view(request):
    data = init()
    template = 'maps-admin/data/data-datasubtypes.html'
    return render_to_response(template, data, context_instance=RequestContext(request))


def data_settings_view(request):
    data = init()
    template = 'maps-admin/data/data-settings.html'
    return render_to_response(template, data, context_instance=RequestContext(request))


def next_viz(request):
    data = {}
    obj_id = request.GET.get('id', None)

    if obj_id:
        data_set = Data.objects.filter(import_id=obj_id)
        data['fields'] = data_set[0]._fields_ordered
        data['data_set'] = data_set
        data['step2'] = True
        return HttpResponse(json.dumps(data), content_type="application/json")

    return HttpResponse(json.dumps({'data': ''}), content_type="application/json")


def get_map(request, id):
    features = []
    results = Data.objects.filter(import_id=id)

    try:
        for res in results:
            temp = json.loads(res.to_json())
            # 1. remove _id
            del temp['_id']

            # 2. build geometry
            geometry = {
                'type': temp['geometry_type'],
                'coordinates': temp['coordinates']
            }
            del temp['geometry_type']
            del temp['coordinates']

            # 3. the remaining items are properties
            properties = temp
            features.append({
                'type': 'Feature',
                'geometry': geometry,
                'properties': properties
            })

        return HttpResponse(json.dumps({'type': 'FeatureCollection', 'features': features}),
                            content_type="application/json")
    except KeyError:
        return HttpResponse(json.dumps({'error': 'invalid data'}), content_type="application/json")


class Partial(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        template_name = kwargs['template_name']

        if template_name.endswith("/"):
            template_name = template_name[:-1]
        self.template_name = 'maps-admin/data/partials/%s.html' % (
            template_name)
        return super(Partial, self).dispatch(request, *args, **kwargs)
