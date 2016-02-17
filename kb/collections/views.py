from django.http import JsonResponse, HttpResponse

from .models import LearningUnit

def learning_units(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    units = []
    for unit in LearningUnit.objects.all():
        units.append({
            'id': unit.pk,
            'label': unit.label
        })

    return JsonResponse({'units': units})
