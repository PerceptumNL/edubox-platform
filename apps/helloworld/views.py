from django.shortcuts import render

def index(request):
    prefix = request.GET.get("Prefix")
    settings = {}
    if prefix != None:
        settings["prefix"] = prefix
    return render(request, "helloworld/index.html",
            {"name": request.user.username,
            "settings": settings})
