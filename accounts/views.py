from django.http import HttpResponse, JsonResponse

from kb.helpers import unpack_token
from kb.apps.models import App

def get_user_info(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    name = request.user.profile.full_name.strip()
    if not name and request.user.profile.alias:
        name = request.user.profile.alias.split('@')[0]
    elif not name:
        name = request.user.username.split('@')[0]

    return JsonResponse({'info': {'name': name }})

def login_user_into_app(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    token = request.GET.get('token', None)
    if token is None:
        return HttpResponse(status=400)

    unpacked = unpack_token(token)
    if unpacked is None:
        return HttpResponse(status=400)

    if int(unpacked['user']) != request.user.pk:
        return HttpResponse(status=403)

    try:
        app = App.objects.get(pk=unpacked['app'])
    except App.DoesNotExist:
        return HttpResponse(status=400)

    from connectors import get_app_connector
    connector = get_app_connector(app)
    if connector is None:
        return HttpResponse(status=500)

    if connector.is_logged_in(token=token):
        return HttpResponse(status=200)

    credentials = connector.get_or_create_credentials(
        token, request.user, app.pk)
    if credentials is None:
        return HttpResponse(status=503)

    if connector.login(token, credentials):
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)
