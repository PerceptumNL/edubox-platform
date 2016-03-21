from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User

from .forms import *
#from .importers import EdeXmlImporter

from kb.models import UserProfile
from kb.groups.models import Institute, Membership, Role
from kb.groups.helpers import generate_password
from .models import *

from bs4 import BeautifulSoup, element
import csv

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
                    'AND '.join(form.errors),)})
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
                institute).order_by('date_added').first().dump)

            #TODO: Fix this, very inefficient
            teacher_email = {(t.full_name if t.is_teacher() else ''): (t.email if t.is_teacher() else '') for t in 
                UserProfile.objects.filter(institute=institute)}
            
            teacher_guess = {}
            for t in soup.leerkrachten.findAll('leerkracht'):
                name = _full_name(t)
                if name in teacher_email:
                    pass
                elif type(t.emailadres) is element.Tag:
                    teacher_email[name] = t.emailadres.string.strip()
                else:
                    #TODO: Should be teacher_guess, to be filled in the form
                    teacher_email[name] = _generate_email(t, form.cleaned_data,
                        institute.email_domain)
            
            return render(request, 'emails.html', {'emails': teacher_email})
        else:
            return render(request, 'done.html', {
                'error': "The submitted form was not valid: (%s)" % (
                    'AND '.join(form.errors),)})
    else:
        form = InstituteForm()
    return render(request, 'upload.html', {'form': form})

def _full_name(node):
    full = ''
    
    first = _tag_string(node.roepnaam)
    if first == '':
        first = _tag_string(node.voornamen)
    if first == '':
        first = _tag_string(node.voorletters)
    full += first +' '

    prefix = _tag_string(node.voorvoegsel)
    if prefix != '':
        full += prefix +' '
    
    full += _tag_string(node.achternaam)
    
    return full

def _tag_string(node):
    if type(node) is element.Tag:
        return node.string.strip().lower()
    return ''

def _generate_email(node, form, domain): 
    email = ''
    
    first = _tag_string(node.roepnaam)
    if first == '':
        first = _tag_string(node.voornamen)
    
    if form['first_name'] == 'name':
        email += first
    elif form['first_name'] == 'letter':
        email += first[0]
    elif form['first_name'] == 'initials':
        email += _tag_string(node.voorletters)
    email += form['separator']

    prefix = _tag_string(node.voorvoegsel)
    if form['prefix'] and prefix != '':
        email += prefix + form['separator']
    
    email += _tag_string(node.achternaam)

    email += '@' + domain
    
    return email

def process_teachers(request): 
    if not request.user.is_staff:
        return HttpResponse(status=401)
            
    if request.method == 'POST':
        form = InstituteForm(request.POST)
        if form.is_valid():
            pass 
        else:
            return render(request, 'done.html', {
                'error': "The submitted form was not valid: (%s)" % (
                    'AND '.join(form.errors),)})
    else:
        form = InstituteForm()
    return render(request, 'upload.html', {'form': form})


#TODO: Turn into DB Transaction. @transaction.atomic?
def process_groups(request):
    if not request.user.is_staff:
        return HttpResponse(status=401)
            
    if request.method == 'POST':
        form = EdeXmlForm(request.POST, request.FILES)
        if form.is_valid():
            pass
        else:
            return render(request, 'done.html', {
                'error': "The submitted form was not valid: (%s)" % (
                    'AND '.join(form.errors),)})
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
        """ 
        return render(request, 'done.html', {
                'teachers': importer.teachers,
                'students': dict(importer.students),
                'institute': importer.institute.title})"""



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
                kwargs['password'] = password

                for key in ['first_name', 'last_name', 'email']:
                    kwargs[key] = form.cleaned_data[key]

                user = User.objects.create_user(**kwargs)
                profile = UserProfile.objects.create(user=user,
                    institute=codecult)

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

