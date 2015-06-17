from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import serializers, viewsets

from .models import App

class AppSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = App
        fields = ('url', 'title', 'icon', 'load_url')

class AppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer

def app_routing(request, app_id):
    return HttpResponse()

def service_routing(request, app_id):
    return HttpResponse()
