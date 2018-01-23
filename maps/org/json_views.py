from rest_framework_mongoengine import generics as Mongo
from .models import Organization
from .serializers import OrganizationSerializer


class AddOrganization(Mongo.ListCreateAPIView):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()


class UpdateOrganization(Mongo.RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
