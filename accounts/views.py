from django.http import HttpResponse

from importlib import import_module

from kb.helpers import unpack_token
from kb.apps.models import App
from router.models import ServerCredentials

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

    adaptor = get_app_adaptor(app)
    if adaptor is None:
        return HttpResponse(status=500)

    if adaptor.is_logged_in(token=token):
        return HttpResponse(status=200)

    credentials = adaptor.get_or_create_credentials(
        token, request.user, app.pk)
    if credentials is None:
        return HttpResponse(status=503)

    if adaptor.login(token, credentials):
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)

def get_app_adaptor(app):
    if not app.adaptor_class:
        return None

    adaptor_path = app.adaptor_class.split('.')
    adaptor_module = ".".join(adaptor_path[:-1])
    if adaptor_module:
        try:
            adaptor = getattr(import_module(adaptor_module),
                adaptor_path[-1])
        except ImportError:
            return None
        except AttributeError:
            return None
    else:
        try:
            adaptor = globals()[adaptor_path[-1]]
        except KeyError:
            return None
    return adaptor
