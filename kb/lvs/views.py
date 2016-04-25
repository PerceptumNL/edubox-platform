from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.forms import formset_factory
from django.db import transaction

from bs4 import BeautifulSoup, element
import csv

from kb.models import UserProfile
from kb.groups.models import Institute, Membership, Role
from kb.groups.helpers import generate_password
from .forms import *
from .models import *
from .helpers import *
from .importers import *

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
            request.session['institute'] = institute.pk
            
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
            request.session['email_edits'] = {elem['name']: elem['email']
                for elem in formset.cleaned_data}
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
    
    if not request.user.is_staff:
        return HttpResponse(status=401)

    if 'emails' not in request.session or 'email_edits' not in \
        request.session or 'institute' not in request.session:
        return HttpResponse(status=400)
    
    GroupFormSet = formset_factory(GroupForm, extra=0)
    if request.method == 'POST':
        formset = GroupFormSet(request.POST)
        if formset.is_valid():
            request.session['group_select'] = {elem['group']: elem['create']
                for elem in formset.cleaned_data}
            return HttpResponseRedirect('/lvs/process/4')
        else:
            return render(request, 'done.html', {
                'error': "The submitted form was not valid: (%s)" % (
                    ' AND '.join(formset.errors),)})
   
    else:
        soup = BeautifulSoup(XmlDump.objects.filter(institute=
            Institute.objects.get(pk=request.session['institute'])).order_by(
            '-date_added').first().dump)

        valid_groups = []
        for t in soup.leerkrachten.findAll('leerkracht'):
            name = full_name(t)
            if name in request.session['emails'] or \
                '@' in request.session['email_edits'].get(name, ''):
                
                for g in t.groepen.findAll('groep'):
                    valid_groups.append(g['key'])

        group_selection = {}
        group_no_option = {}
        for g in soup.edex.groepen.findAll('groep'):
            group = g.naam.string +' : '+ g.jaargroep.string
            if g['key'] in valid_groups:
                group_selection[group] = g['key']
            else:
                group_no_option[group] = g['key']
        
        formset = GroupFormSet(initial=[{'group': k, 
            'create': 'import'} for k in group_selection])
        
        request.session['groups'] = group_selection

    return render(request, 'groups.html', {'formset': formset, 'no_option':
        group_no_option})
   

def process_transaction(request):
    if not request.user.is_staff:
        return HttpResponse(status=401)

    if 'emails' not in request.session or 'email_edits' not in \
        request.session or 'institute' not in request.session or 'groups' not \
        in request.session or 'group_select' not in request.session:
        return HttpResponse(status=400)
   
    groups = {}
    teachers = {}
    students = {}

    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            request.session['password'] = form.cleaned_data['password']
            
            return HttpResponseRedirect('/lvs/process/5')
        else:
            return render(request, 'done.html', {
                'error': "The submitted form was not valid: (%s)" % (
                    ' AND '.join(form.errors),)})
    else:
        institute = Institute.objects.get(pk=request.session['institute'])
        
        soup = BeautifulSoup(XmlDump.objects.filter(institute=
            institute).order_by('-date_added').first().dump)

        for k, v in request.session['group_select'].items():
            if v == 'import':
                groups[request.session['groups'][k]] = (k, [], [])

        for t in soup.leerkrachten.findAll('leerkracht'):
            name = full_name(t)
            username = t['key'] +'@'+str(institute.pk)
            existing_user = User.objects.filter(username=username)
            flag = False
            
            for g in t.findAll('groep'):
                if g['key'] in groups:
                    groups[g['key']][1].append(name)
                    flag = True
            
            if not len(existing_user) == 1 and flag:
                if name in request.session['emails']:
                    teachers[t['key']] = (name, request.session['emails'][name])
                elif '@' in request.session['email_edits'].get(name, ''):
                    teachers[t['key']] = (name, request.session['email_edits'][name])

        for s in soup.edex.findAll('leerling'):
            name = full_name(s)
            username = s['key'] +'@'+str(institute.pk)
            existing_user = User.objects.filter(username=username)

            if g['key'] in groups:
                groups[s.groep['key']][2].append(name)
            
                if not len(existing_user) == 1:
                    students[s['key']] = (name, EdeXmlImporter._generate_alias(s,
                        institute))
        
        request.session['group_list'] = list(groups.keys())
        request.session['teacher_list'] = list(teachers.keys())
        request.session['student_list'] = list(students.keys())
        
        form = PasswordForm()
    return render(request, 'confirm.html', {'form': form, 'groups': groups,
        'teachers': teachers.values(), 'students': students.values()})


@transaction.atomic
def process_commit(request):
    """This is just a placeholder function, containg some relevant parts of
    the previous functions: It should in no way be considered a functional
    implementation.

    generated using a DB Transaction (@transaction.atomic).

    Finally confirming this screen should lead to the DB being changed and 
    downloading a zipfile of CSV-files (one for each new group)
    """

    if not request.user.is_staff:
        return HttpResponse(status=401)

    try:
        institute = Institute.objects.get(pk=request.session['institute'])
        emails = request.session['email_edits']
        groups = request.session['group_list']
        teachers = request.session['teacher_list']
        students = request.session['student_list']
        password = request.session['password']
    except KeyError:
        return HttpResponse(status=400)
    
    xml = XmlDump.objects.filter(institute=institute).order_by('-date_added'
        ).first().dump
    
    importer = EdeXmlImporter(xml, institute, emails, groups, teachers,
        students, password)
    importer.parse_all()
    
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

