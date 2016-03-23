from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password 

from .forms import EdeXmlForm, CodecultStudentForm
from .importers import EdeXmlImporter

from kb.models import UserProfile
from kb.groups.models import Institute, Membership, Role
from kb.groups.helpers import generate_password

import csv

def upload_edexml(request):
    if not request.user.is_staff:
        return HttpResponse(status=401)

    if request.method == 'POST':
        form = EdeXmlForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                importer = EdeXmlImporter(
                    request.FILES['edexml'], form.cleaned_data)
                importer.parse_all()
            except Exception as e:
                from django.conf import settings
                if settings.DEBUG:
                    raise e
                return render(request, 'done.html', {
                    'error': "An error occured while importing: '%s'" % (e,)})
            else:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = \
                    'attachment; filename={}.csv'.format(importer.institute.title)

                writer = csv.writer(response)
                writer.writerow([importer.institute.title])
                writer.writerow(['Docenten'])
                for t in importer.teachers:
                    writer.writerow(t)
                writer.writerow(['Leerlingen'])
                for g, s in sorted(importer.students.items()):
                    writer.writerow([g])
                    for m in s:
                        writer.writerow(m)
                return response
                """ 
                return render(request, 'done.html', {
                        'teachers': importer.teachers,
                        'students': dict(importer.students),
                        'institute': importer.institute.title})"""
        else:
            return render(request, 'done.html', {
                'error': "The submitted form was not valid: (%s)" % (
                    'AND '.join(form.errors),)})
    else:
        form = EdeXmlForm()
    return render(request, 'upload.html', {'form': form})

def add_student(request):
    if not request.user.is_staff:
        return HttpResponse(status=401)

    if request.method == 'POST':
        kwargs = {}
        form = CodecultStudentForm(request.POST)
        if form.is_valid():
            try:
                codecult = Institute.objects.get(title='CodeCult')
                name = EdeXmlImporter._join_names(
                    form.cleaned_data['first_name'],
                    form.cleaned_data['last_name'])

                user_count = len(User.objects.filter(username__regex=r'^'+
                    name+'.*'+codecult.email_domain+'$'))
                if user_count > 0:
                    name += str(user_count+1)
                kwargs['username'] = name+'@'+codecult.email_domain

                password = form.cleaned_data['password']
                if password == '':
                    password = generate_password()
                kwargs['password'] = make_password(password)

                for key in ['first_name', 'last_name', 'email']:
                    kwargs[key] = form.cleaned_data[key]

                user = User.objects.create(**kwargs)
                profile = UserProfile.objects.create(user=user,
                    institute=codecult)
                kwargs['password'] = password

                Membership.objects.create(user=profile, 
                    group=form.cleaned_data['group'], 
                    role=Role.objects.get(role='Student'))

            except Exception as e:
                from django.conf import settings
                if settings.DEBUG:
                    raise e
                return render(request, 'student.html', {
                    'error': "An error occured while importing: '%s'" % (e,)})
            else:
                return render(request, 'student.html', {
                        'data': [(e, kwargs[e]) for e in ['first_name', 
                            'last_name', 'email', 'username', 'password']]})
        else:
            return render(request, 'student.html', {
                'error': "The submitted form was not valid: (%s)" % (
                    'AND '.join(form.errors),)})
    else:
        form = CodecultStudentForm()
    return render(request, 'upload.html', {'form': form})

