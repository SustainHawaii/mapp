from django.conf import settings
from maps.django_mapp.mixins import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from maps.core import api
from django.core.mail import send_mail
from maps.users.models import User
from maps.locations.models import LocationType

role = 'maps-admin'
data = {}


def index_view(request):
    data['role'] = role
    data['loc_types'] = LocationType.objects
    #data['tags'] = api.tags.get()
    #data['categories'] = api.taxonomy.get()
    #data['viz'] = api.dataviz.get()
    return render_to_response('homepage/index.html', data,
                              context_instance=RequestContext(request)
                              )

def loginadmin_view(request):
    data['role'] = role
    #data['loc_types'] = LocationType.objects
    #data['tags'] = api.tags.get()
    #data['categories'] = api.taxonomy.get()
    #data['viz'] = api.dataviz.get()
    return render_to_response('homepage/loginadmin.html', data,
                              context_instance=RequestContext(request)
                              )

def register_view(request):
    data['role'] = role
    #data['loc_types'] = LocationType.objects
    #data['tags'] = api.tags.get()
    #data['categories'] = api.taxonomy.get()
    #data['viz'] = api.dataviz.get()
    return render_to_response('homepage/register.html', data,
                              context_instance=RequestContext(request)
                              )

def lostpassword_view(request):
    data['role'] = role
    #data['loc_types'] = LocationType.objects
    #data['tags'] = api.tags.get()
    #data['categories'] = api.taxonomy.get()
    #data['viz'] = api.dataviz.get()
    return render_to_response('homepage/lostpassword.html', data,
                              context_instance=RequestContext(request)
                              )    


def index_directory_view(request):
    data['role'] = role
    return render_to_response('homepage/index-directory.html', data, context_instance=RequestContext(request))


def visualizations_view(request):
    data['role'] = role
    data['loc_types'] = api.locationtypes.get().get("results")
    data['tags'] = api.tags.get()
    data['categories'] = api.taxonomy.get()
    data['viz'] = api.dataviz.get()
    return render_to_response('homepage/viz.html', data, context_instance=RequestContext(request))


def members_view(request):
    data['role'] = role
    data['orgs'] = api.org.get()
    data['users'] = api.users.get()
    return render_to_response('homepage/members.html', data, context_instance=RequestContext(request))


def members_profile_view(request, id):
    data['role'] = role
    member_type = request.GET.get('type', None)
    if member_type == 'org':
        data['member'] = api.org.get(id=id)
        data['loc'] = Location.objects.filter(org__contains=id)
    elif member_type == 'user':
        data['member'] = User.objects.get(id=id)
        data['loc'] = []

    tags = []
    for l in data['loc']:
        if l['tags']:
            try:
                for tag in json.loads(l['tags']):
                    if not tag in tags:
                        tags.append(tag)
            except:
                pass
    data['tags'] = tags

    cats = []
    for tag in tags:
        for cat in Categories.objects.filter(name=tag):
            tax = json.loads(cat.taxonomies)
            for k in tax:
                if tax[k]:
                    obj = Taxonomy.objects.get(id=k)
                    if obj.name not in cats:
                        cats.append(obj.name)
    data['categories'] = cats

    return render_to_response('homepage/members-profile.html', data, context_instance=RequestContext(request))


def members_location_view(request, id):
    from maps.categories.models import Categories
    data['role'] = role
    data['object'] = Location.objects.get(id=id)
    data['owner'] = data['object'].created_by
    data['user'] = request.user
    try:
        data['frontforms'] = data['object'].frontend_form()[0]['field_groups']
    except IndexError:
        print('Location has no frontend forms')

    data['categories'] = Categories.for_object(data['object'])


    return render_to_response('homepage/members-location.html', data, context_instance=RequestContext(request))


def about_view(request):
    data['role'] = role

    if request.method == 'POST':
        name = request.POST.get('name', None)
        body = request.POST.get('body', None)
        from_email = request.POST.get('email', None)
        subject = request.POST.get('subject', None)
        subject = 'Message from ' + name + ': ' + subject

        send_mail(subject, body, from_email, settings.CONTACT_FORM_RECIPIENT)

    return render_to_response('homepage/about.html', data, context_instance=RequestContext(request))


