from django.shortcuts import render

def index(request):
    return render(request, "helloworld/index.html",
            {"name": request.user.username,
            "prefix": request.GET.get("Prefix")})
