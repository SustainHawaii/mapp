from models import *
from serializers import *
from rest_framework_mongoengine import generics as Mongo
from mongoengine.queryset import Q
from maps.locations.json_views import build_geojson_for_googlemaps
from rest_framework.response import Response
import json
from bson import json_util
from django.http import HttpResponse

class AddDataImport(Mongo.ListCreateAPIView):
    serializer_class = DataImportSerializer
    queryset = DataImport.objects.all()

    def get_serializer_class(self):
        list_type = self.request.QUERY_PARAMS.get('list_type', None)
        if list_type == "simple":
            return DataImportSimpleSerializer
        return self.serializer_class


class UpdateDataImport(Mongo.RetrieveUpdateDestroyAPIView):
    serializer_class = DataImportSerializer
    queryset = DataImport.objects.all()


class BulkRetrieveGeoJson(Mongo.MongoAPIView):

    def get(self, request, *args, **kwargs):
        import_ids = request.GET.getlist('import_id[]')
        if import_ids:
            data = Data.objects.filter(import_id__in=import_ids)
        else:
            data = Data.objects.all()

        geojson = build_geojson_for_googlemaps(data)
        return Response(geojson)


class BulkRetrieveData(Mongo.ListAPIView):
    serializer_class = DataSerializer
    paginate_by = 10
    paginate_by_param = 'page_size'
    max_paginate_by = 200

    def get_queryset(self):
        import_ids = self.request.QUERY_PARAMS.get('import_ids')
        order_by = self.request.QUERY_PARAMS.get('order_by')
        search = self.request.QUERY_PARAMS.get('search')
        search_fields = self.request.QUERY_PARAMS.get('search_fields')
        data_format = self.request.QUERY_PARAMS.get('data_format')

        if import_ids:
            queryset = Data.objects.filter(import_id__in=import_ids.split(","))
        else:
            queryset = Data.objects.all()

        if (search and search_fields):
            print(search_fields)
            # or the searches together for each field in search_fields
            qset = Q()
            for field in search_fields.split(","):
                qset = qset | Q(**{field + "__icontains": search})

            queryset = queryset.filter(qset)

        if order_by:
            queryset = queryset.order_by(order_by)
        # return Data.objects.filter(import_id=import_id)

        return queryset


class RetrieveData(Mongo.ListAPIView):
    serializer_class = DataSerializer

    def get_queryset(self):
        import_id = self.kwargs['import_id']
        limit = self.request.QUERY_PARAMS.get('limit')
        order_by = self.request.QUERY_PARAMS.get('order_by')
        queryset = Data.objects.filter(import_id=import_id)
        if order_by:
            queryset = queryset.order_by(order_by)
        if limit:
            # note this will blow chunck is limit is non numeric
            # return Data.objects.filter(import_id=import_id)[:int(limit)]
            queryset = queryset[:int(limit)]
        # return Data.objects.filter(import_id=import_id)
        return queryset


def datatable(request, import_id):
    start = int(request.GET['iDisplayStart'])
    length = int(request.GET['iDisplayLength'])
    sEcho = int(request.GET['sEcho'])

    # get fields
    fields_query = Data.objects.filter(import_id=import_id)[0]
    fields = fields_query._fields_ordered 
    print fields
    fields = [x for x in fields if x not in ('id', 'import_id')]
    
    #get total database count
    query = Data.objects.filter(import_id=import_id)
    total = query.count()

    #filter by serach parameters
    '''
    search_param = request.GET.get('sSearch', None)
    if search_param:
        query.filter(Q(name__icontains=search_param) |
                     Q(description__icontains=search_param))
    total_display = len(query)

    '''

    #search parameters
    sort_col = request.GET.get('iSortCol_0', 99)
    sort_order = request.GET.get('sSortDir_0', None)
    if sort_col < len(fields):
        order_by = fields[sort_col]
        if sort_order == "desc":
            order_by = "-" + order_by
        query.order_by(order_by)

    
    #now limit the size of the mongo results
    query = query[start:start + length]


    #qry is the data object definitions that go into the table
    #we are now converting our mongo Documents, to a the representation
    #needed for the datatable


    table_data = []
    for q in query:
        row = []
        for f in fields:
             row.append(q[f])
        table_data.append(row)

    # has edit permission
    '''OtherEdit = request.user.has_edit_other_permission("category") 
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
    '''
    response = {
        "aaData": table_data,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total,
        "sEcho": sEcho,
    }
    response = json.dumps(response, default=json_util.default)

    return HttpResponse(
        response,
        content_type='application/json'
    )


