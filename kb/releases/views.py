from django.http import JsonResponse

def release_list(request):
    from .models import Release

    delivered_only = bool(int(request.GET.get('delivered', '0')))

    if delivered_only:
        releases = Release.objects.filter(show=True, delivered=True)
    else:
        releases = Release.objects.filter(show=True)
    release_list = []
    for release in releases:
        release_list.append({
            'major': release.major,
            'minor': release.minor,
            'patch': release.patch,
            'delivered': release.delivered,
            'scheduled': (release.scheduled.strftime("%d-%m-%Y") if
                release.scheduled else None),
            'description': release.description or None,
            'items': [{ 'type': item.get_item_type_display(),
                        'description': item.description }
                        for item in release.items.filter(show=True)]})

    return JsonResponse({'releases': release_list})
