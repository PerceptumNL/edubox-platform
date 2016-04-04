from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.forms import formset_factory

from bs4 import BeautifulSoup, element
import csv

from kb.models import UserProfile
from kb.groups.models import Institute, Membership, Role
from kb.groups.helpers import generate_password
from .forms import *
from .models import *
from .helpers import *

def upload_edexml(request):
    if not request.user.is_staff:
        return HttpResponse(status=401)

    if request.method == 'POST':
        form = EdeXmlForm(request.POST, request.FILES)
        if form.is_valid():
            soup = BeautifulSoup(request.FILES['edexml'])
            institute = form.cleaned_data['institute']

            try:
                xmldump = XmlDump.objects.create(dump=str(soup.edex))
            except Exception:
                xmldump = XmlDump.objects.create(dump=str(soup))

            institute.xmls.add(xmldump)
            return render(request, 'done.html', {'institute': institute})

        else:
            return render(request, 'done.html', {
                'error': "The submitted form was not valid: (%s)" % (
                    ' AND '.join(form.errors),)})
    else:
        form = EdeXmlForm()
    return render(request, 'upload.html', {'form': form})

def process_institute(request):
    if not request.user.is_staff:
        return HttpResponse(status=401)

    if request.method == 'POST':
        form = InstituteForm(request.POST, request.FILES)
        if form.is_valid():
            institute = form.cleaned_data['institute']
            soup = BeautifulSoup(XmlDump.objects.filter(institute=
                institute).order_by('-date_added').first().dump)

            teacher_email = {t.full_name: t.email for t in
                UserProfile.objects.filter(institute=institute, is_teacher=True)}

            teacher_guess = {}
            for t in soup.leerkrachten.findAll('leerkracht'):
                name = full_name(t)
                if name in teacher_email:
                    pass
                elif type(t.emailadres) is element.Tag:
                    teacher_email[name] = t.emailadres.string.strip()
                else:
                    teacher_guess[name] = generate_email(t, form.cleaned_data,
                        institute.email_domain)
            request.session['emails'] = teacher_email
            request.session['guesses'] = teacher_guess
            
            return HttpResponseRedirect('/lvs/process/2')
        else:
            return render(request, 'done.html', {
                'error': "The submitted form was not valid: (%s)" % (
                    ' AND '.join(form.errors),)})
    else:
        form = InstituteForm()
    return render(request, 'upload.html', {'form': form})


def process_teachers(request): 
    if not request.user.is_staff:
        return HttpResponse(status=401)

    if 'emails' not in request.session or 'guesses' not in request.session:
        return HttpResponse(status=400)

    EmailFormSet = formset_factory(EmailForm, extra=0)
    if request.method == 'POST':
        formset = EmailFormSet(request.POST)
        if formset.is_valid():
            request.session['email_edits'] = formset.cleaned_data
            return HttpResponseRedirect('/lvs/process/3')
        else:
            return render(request, 'done.html', {
                'error': "The submitted form was not valid: (%s)" % (
                    ' AND '.join(formset.errors),)})
    else:
        formset = EmailFormSet(initial=[{'name': k, 'email': v} for k, v in 
            request.session['guesses'].items()])

    return render(request, 'emails.html', {'emails': request.session['emails'],
        'formset': formset})

def process_groups(request):
    """This is just a placeholder function, containg some relevant parts of
    the previous functions: It should in no way be considered a functional
    implementation.

    The idea is this view should provide an overview of:
    1. Already existing groups from the institute
    2. Groups that could be created (checkbox option)
    3. Groups that can't be created because no teacher email is present
    4. Textbox for password for new created users

    This should then provide an overview screen of all changes to be made,
    generated using a DB Transaction (@transaction.atomic).

    Finally confirming this screen should lead to the DB being changed and 
    downloading a zipfile of CSV-files (one for each new group)
    """
    
    if not request.user.is_staff:
        return HttpResponse(status=401)

    return render(request, 'emails.html', request.session)
    
    if request.method == 'POST':
        form = EdeXmlForm(request.POST, request.FILES)
        if form.is_valid():
            pass
        else:
            return render(request, 'done.html', {
                'error': "The submitted form was not valid: (%s)" % (
                    ' AND '.join(form.errors),)})
    else:
        form = EdeXmlForm()
    return render(request, 'upload.html', {'form': form})
    
    try:
        importer = EdeXMLImporter
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

        return render(request, 'done.html', {
                'teachers': importer.teachers,
                'students': dict(importer.students),
                'institute': importer.institute.title})



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
                    form.cleaned_data['last_name_prefix'],
                    form.cleaned_data['last_name'])

                user_count = len(User.objects.filter(username__regex=r'^'+
                    name+'.*'+str(codecult.pk)+'$'))
                if user_count > 0:
                    name += str(user_count+1)
                kwargs['username'] = name+'@'+str(codecult.pk)

                password = form.cleaned_data['password']
                if password == '':
                    password = generate_password()
                kwargs['password'] = password

                for key in ['first_name', 'last_name', 'email']:
                    kwargs[key] = form.cleaned_data[key]

                user = User.objects.create_user(**kwargs)
                profile = UserProfile.objects.create(user=user,
                    institute=codecult,
                    alias=name+'@'+codecult.email_domain,
                    surname_prefixes=form.cleaned_data['last_name_prefix'])
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
                res = [('first_name', kwargs['first_name'])]
                res.append(('last_name', form.cleaned_data['last_name_prefix']+
                    ' '+kwargs['last_name']))
                res.append(('username', name+'@'+codecult.email_domain))
                res += [(e, kwargs[e]) for e in ['email', 'password']]
                return render(request, 'student.html', {
                        'data': res})
        else:
            return render(request, 'student.html', {
                'error': "The submitted form was not valid: (%s)" % (
                    ' AND '.join(form.errors),)})
    else:
        form = CodecultStudentForm()
    return render(request, 'upload.html', {'form': form})

