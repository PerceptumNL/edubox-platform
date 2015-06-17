from django.http import HttpResponse

def handle(request):
    if request.method == "POST":
        return HttpResponse(request.body)
    else:
        return HttpResponse(status=405)
