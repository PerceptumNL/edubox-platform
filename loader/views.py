from django.shortcuts import render
from rest_framework import serializers, viewsets

from .models import App

class AppSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = App
        fields = ('url', 'title', 'icon')

class AppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer
