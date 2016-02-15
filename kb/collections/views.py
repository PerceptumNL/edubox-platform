from rest_framework import serializers, viewsets
from .models import LearningUnit

class LearningUnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LearningUnit
        fields = ('id', 'label')


class LearningUnitViewSet(viewsets.ModelViewSet):
    #TODO: extend queryset to filter completed and unreachable.
    queryset = LearningUnit.objects.all()
    serializer_class = LearningUnitSerializer
