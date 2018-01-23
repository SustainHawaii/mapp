from maps.data_visualization.serializers import DataVisualizationSerializer
from maps.data_visualization.models import DataVisualization
from rest_framework_mongoengine import generics as mongo
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
from mongoengine.django.shortcuts import get_document_or_404


def get_shorturl(request, id):
    domain = request.get_host()  # check for short url
    if "127.0" in domain.split(":")[0]:
        domain = "http://softworks.com.my"

    longUrl = domain + "/maps-admin/data/share-viz/" + id + "/"
    bitlyRequest = ("https://api-ssl.bitly.com/v3/shorten?access_token=" +
                    settings.BITLY_API + "&longUrl=" + longUrl +
                    "&domain=j.mp&format=txt")

    return requests.get(bitlyRequest).text.rstrip()


@api_view(['GET'])
def shortUrl(request, id):
    dataviz = get_document_or_404(DataVisualization, id=id)
    if not dataviz.short_url:

        mydict = {"url": get_shorturl(request, id)}
    else:
        mydict = {"url": "short_url"}

    response = Response(mydict["url"])
    return response


class AddDataViz(mongo.ListCreateAPIView):
    serializer_class = DataVisualizationSerializer
    #we use hidden to hide dataviz, like the ones we use to display maps for
    #resources
    queryset = DataVisualization.objects.filter(hidden=False)

    def post(self, request, *args, **kwargs):
        try:
            DataVisualization.objects.get(group_name=request.DATA['group_name'])        
        except:
            return self.create(request, *args, **kwargs)    
        return Response({'error': 'This group_name is not unique'}, status=status.HTTP_400_BAD_REQUEST)            

    def post_save(self, obj, created=False):
        if created:
            obj.short_url = get_shorturl(self.request, str(obj.id))
            obj.save()


class UpdateDataViz(mongo.RetrieveUpdateDestroyAPIView):
    serializer_class = DataVisualizationSerializer
    queryset = DataVisualization.objects
