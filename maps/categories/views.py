from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from api_view import *
from mappweb.settings import PRIVACY_OPTION
from django.shortcuts import render_to_response
from maps.locations.models import Location
#the following are needed for datatable method
import collections
import operator
from maps.core.views import LinkBuilder 
from bson import json_util
import json
from django.http import HttpResponse
from mongoengine.queryset.visitor import Q

role = 'maps-admin'
template_base_path = 'maps-admin/categories/'

def init_data():
    return {
        'role': role,
    }


@login_required(login_url='/')
def category(request):
    data = init_data()
    data['data'] = Categories.objects.all()[:10]
    data['data_2'] = Taxonomy.objects.all()[:10]
    return render_to_response(template_base_path + 'categories.html', data, context_instance=RequestContext(request))


@login_required(login_url='/')
# @api_view(['POST', 'GET'])
def category_add(request):
    data = init_data()
    data['privacy'] = PRIVACY_OPTION
    return render_to_response(template_base_path + 'categories-addcategory.html', data, context_instance=RequestContext(request))


@login_required(login_url='/')
# @api_view(['GET', 'POST'])
def category_update(request, cat_id):
    data = init_data()
    data['data'] = Categories.objects.get(id=cat_id)
    return render_to_response(template_base_path + 'categories-addcategory.html', data, context_instance=RequestContext(request))


@login_required(login_url='/')
# @api_view(['GET', 'POST'])
def taxonomy_add(request):
    data = init_data()
    data['privacy'] = PRIVACY_OPTION
    data['location'] = Location.objects.all()
    return render_to_response(template_base_path + 'categories-addtaxonomy.html', data, context_instance=RequestContext(request))


@login_required(login_url='/')
# @api_view(['GET', 'POST'])
def taxonomy_update(request, tax_id):
    data = init_data()
    data['privacy'] = PRIVACY_OPTION
    data['data'] = Taxonomy.objects.get(id=tax_id)
    return render_to_response(template_base_path + 'categories-addtaxonomy.html', data, context_instance=RequestContext(request))


def tags_datatable(request):
    start = int(request.GET['iDisplayStart'])
    length = int(request.GET['iDisplayLength'])
    sEcho = int(request.GET['sEcho'])

    #get total database count
    query = Categories.objects.all()
    total = query.count()

    #filter by serach parameters
    search_param = request.GET.get('sSearch', None)
    if search_param:
        query.filter(Q(name__icontains=search_param) |
                     Q(description__icontains=search_param))
    total_display = len(query)


    #search parameters
    dt_header = ['name', 'number_using', 'last_updated']
    sort_col = request.GET.get('iSortCol_0', 99)
    sort_order = request.GET.get('sSortDir_0', None)
    if sort_col < len(dt_header):
        order_by = dt_header[sort_col]
        if sort_order == "desc":
            order_by = "-" + order_by
        query.order_by(order_by)

    #now limit the size of the mongo results
    query = query[start:start + length]


    #qry is the data object definitions that go into the table
    #we are now converting our mongo Documents, to a the representation
    #needed for the datatable

    # has edit permission
    OtherEdit = request.user.has_edit_other_permission("category") 
    OtherDel = request.user.has_delete_other_permission("category") 
    OwnEdit = request.user.has_edit_own_permission("category") 
    OwnDel = request.user.has_delete_own_permission("category") 

    if any([OtherEdit, OtherDel, OwnEdit, OwnDel]):
        link_builder = LinkBuilder(request.user,
                               "/maps-admin/categories/update-category/",
                                "category",
                                "delete_cat")
        query = [
            (
                link_builder.view_link(q),
                q.number_using,
                q.updated,
                link_builder.edit_link(q) +
                link_builder.del_link(q)
            ) for q in query
        ]
    else:
        query = [("No Permissions")]

    response = {
        "aaData": query,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total_display,
        "sEcho": sEcho,
    }
    response = json.dumps(response, default=json_util.default)

    return HttpResponse(
        response,
        content_type='application/json'
    )


def cats_datatable(request):
    start = int(request.GET['iDisplayStart'])
    length = int(request.GET['iDisplayLength'])
    sEcho = int(request.GET['sEcho'])

    #get total database count
    query = Taxonomy.objects.all()
    total = query.count()

    #filter by serach parameters
    search_param = request.GET.get('sSearch', None)
    if search_param:
        query.filter(Q(name__icontains=search_param) |
                     Q(description__icontains=search_param))
    total_display = len(query)


    #search parameters
    dt_header = ['name', 'number_using','updated']
    sort_col = request.GET.get('iSortCol_0', 99)
    sort_order = request.GET.get('sSortDir_0', None)
    if sort_col < len(dt_header):
        order_by = dt_header[sort_col]
        if sort_order == "desc":
            order_by = "-" + order_by
        query.order_by(order_by)

    #now limit the size of the mongo results
    query = query[start:start + length]


    #qry is the data object definitions that go into the table
    #we are now converting our mongo Documents, to a the representation
    #needed for the datatable

    # has edit permission -taxonomy and category use same permission
    OtherEdit = request.user.has_edit_other_permission("category") 
    OtherDel = request.user.has_delete_other_permission("category") 
    OwnEdit = request.user.has_edit_own_permission("category") 
    OwnDel = request.user.has_delete_own_permission("category") 

    if any([OtherEdit, OtherDel, OwnEdit, OwnDel]):
        link_builder = LinkBuilder(request.user,
                               "/maps-admin/categories/update-taxonomy/",
                                "category",
                                "delete_tax")
        query = [
            (
                link_builder.view_link(q),
                q.number_using,
                q.updated,
                link_builder.edit_link(q) +
                link_builder.del_link(q)
            ) for q in query
        ]
    else:
        query = [("No Permissions")]

    response = {
        "aaData": query,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total_display,
        "sEcho": sEcho,
    }
    response = json.dumps(response, default=json_util.default)

    return HttpResponse(
        response,
        content_type='application/json'
    )
