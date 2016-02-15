from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from .forms import EdeXmlForm
from .importers import EdeXmlImporter

def upload_edexml(request):
    if not request.user.is_staff:
        return HttpResponse(status=401)
    
    if request.method == 'POST':
        form = EdeXmlForm(request.POST, request.FILES)
        if form.is_valid():
            importer = EdeXmlImporter(request.FILES['edexml'], 
                    form.cleaned_data)
            importer.parse_all()
            return render(request, 'done.html', {
                    'teachers': importer.teachers,
                    'students': dict(importer.students),
                    'institute': importer.institute.title})
    else:
        form = EdeXmlForm()
    return render(request, 'upload.html', {'form': form})

