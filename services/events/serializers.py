from rest_framework import serializers

from .models import ReadEvent

class ReadEventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ReadEvent
        fields = ('uuid', 'user', 'verb', 'article', 'app', 'group', 'stored',
                'timestamp')
