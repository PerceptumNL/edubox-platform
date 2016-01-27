from django.http import HttpResponse
from router import AppRouter
from kb.apps.models import App

def sim1(request):
    app = App.objects.get(root="scratch.mit.edu")
    router = AppRouter(app)
    status = router.app_login()
    return HttpResponse('Success: '+str(status))

