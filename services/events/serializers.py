from rest_framework import serializers

from .models import Event

class EventSerializer(serializers.ModelSerializer):
    uuid = UUIDField(read_only=True)
    user = PrimaryKeyRelatedField(queryset=User.objects.all())
    verb = PrimaryKeyRelatedField(queryset=Verb.objects.all())
    
    obj = 
    result = 

    context = PrimaryKeyRelatedField(queryset=Context.objects.all())
    stored = DateTimeField(read_only=True)
    timestamp = DateTimeField()#required=False)
    authority = CharField(max_length=255)
    version = CharField(max_length=255)

    """
    class Meta:
        model = Event
        fields = ('uuid', 'user', 'verb', 'context',
            'stored', 'timestamp', 'authority', 'version')
    """
