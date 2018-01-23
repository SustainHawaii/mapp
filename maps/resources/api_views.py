import json
from rest_framework_mongoengine import generics as Mongo
from utils import save_image
from .models import Resources, Settings
from .serializers import ResourcesSerializer, SettingsSerializer
from maps.data_visualization.models import DataVisualization
from maps.data_visualization.serializers import DataVisualizationSerializer
from rest_framework.response import Response
from rest_framework import status


class ListCreateResources(Mongo.ListCreateAPIView):
    queryset = Resources.objects.all()
    serializer_class = ResourcesSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'layout' in request.DATA:
            self.layout = json.loads(request.DATA['layout'])
            del request.DATA['layout']
        if 'main_map' in request.DATA:
            self.main_map = json.loads(request.DATA['main_map'])
            del request.DATA['main_map']
        return self.create(request, *args, **kwargs)

    def post_save(self, obj, created=False):
        if self.layout:
            obj.layout = self.layout
            obj.save()
        if self.main_map:
            dataviz = DataVisualizationSerializer(data=self.main_map)
            if dataviz.is_valid():
                dataviz.save()
            else:
                print ("we got errors saving dataviz", dataviz.errors)
                return Response(dataviz.errors, status=status.HTTP_400_BAD_REQUEST)
            obj.main_map = dataviz.object
            obj.save()
        
        f = self.request.FILES.get('file', None)
        #which file are we saving?
        if (f):
            file_type = False
            if (f.name == obj.page_background):
                file_type = "page_background_url"
            elif (f.name == obj.page_logo):
                file_type = "page_logo_url"
            if (file_type):
                save_image(f, obj, file_type, 'name', 'resources/')

class RetrieveUpdateDestroyResources(Mongo.RetrieveUpdateDestroyAPIView):

    queryset = Resources.objects.all()
    serializer_class = ResourcesSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if 'layout' in request.DATA:
            self.layout = json.loads(request.DATA['layout'])
            del request.DATA['layout']
        if 'main_map' in request.DATA:
            self.main_map = json.loads(request.DATA['main_map'])
            del request.DATA['main_map']
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def post_save(self, obj, created=False):
        print "post_save"
        if self.layout:
            obj.layout = self.layout
            obj.save()
        if self.main_map:
            dataviz = DataVisualizationSerializer(data=self.main_map)
            if dataviz.is_valid():
                [d.delete() for d in DataVisualization.objects if d.group_name == dataviz.init_data['group_name']]
                dataviz.save()
            else:
                print ("we got errors saving dataviz", dataviz.errors)
                return Response(dataviz.errors, status=status.HTTP_400_BAD_REQUEST)
            obj.main_map = dataviz.object
            obj.save()

        f = self.request.FILES.get('file', None)
        #which file are we saving?
        if (f):
            file_type = False
            if (f.name == obj.page_background):
                file_type = "page_background_url"
            elif (f.name == obj.page_logo):
                file_type = "page_logo_url"
            if (file_type):
                save_image(f, obj, file_type, 'name', 'resources/')


class RetrieveUpdateSettings(Mongo.RetrieveUpdateAPIView):

    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
