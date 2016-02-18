from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from router import AppRouter
from kb.apps.models import App
from datetime import datetime

def sim_login(request, app_id):
    app = get_object_or_404(App, pk=app_id)
    router = AppRouter(app)
    router.request = request
    t1 = datetime.now()
    success = router.app_login()
    dt = datetime.now() - t1
    if success:
        return HttpResponse(
            'Simulating login in %s succeeded in %s' % (app, dt))
    else:
        return HttpResponse(
            'Simulating login in %s failed in %s' % (app, dt))

def sim_signup(request, app_id):
    app = get_object_or_404(App, pk=app_id)
    router = AppRouter(app)
    router.request = request
    t1 = datetime.now()
    success = router.app_signup()
    dt = datetime.now() - t1
    if success:
        return HttpResponse(
            'Simulating signup in %s succeeded in %s' % (app, dt))
    else:
        return HttpResponse(
            'Simulating signup in %s failed in %s' % (app, dt))
