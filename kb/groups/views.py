from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from kb.models import UserProfile
from .models import *
from .forms import StudentForm, TeacherForm
from .helpers import generate_password


from collections import defaultdict

def teacher_form(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = TeacherForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect('load_data/teachers/process/')
    else:
        form = TeacherForm()

    return render(request, 'data_input.html', {'form': form})

def student_form(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = StudentForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect('load_data/students/process/')
    else:
        form = StudentForm()

    return render(request, 'data_input.html', {'form': form})

def process_teachers(request):
    institute = Institute.objects.get(pk=request.POST.get('institute'))
    teachers = request.POST.get('teachers', '').split('\n')
    
    incorrect = []
    id_exists = []
    group_exists = []
    teacher_groups = {}
    teacher_role = Role.objects.get(role='Teacher')

    for line in teachers:
        if line == '':
            continue
        s = line.split(',')
        if len(s) != 4:
            incorrect.append(line)
        else:
            teacher_id, first, last, groups = [e.strip() for e in s]
            groups = [g.strip() for g in groups.split(';')]
            if User.objects.filter(username=teacher_id).exists():
                id_exists.append(line)
            elif any([Group.objects.filter(title=g).exists() for g in groups]):
                group_exists.append(line)
            else:
                pw = generate_password('-')
                
                user = User.objects.create(username=teacher_id,
                        first_name=first, last_name=last,
                        email=teacher_id+'@'+institute.email_domain,
                        password=make_password(pw))
                profile = UserProfile.objects.create(user=user,
                        institute=institute)
                
                for group in groups:
                    code = generate_password('-')
                    group = Group.objects.create(title=group,
                        code=group,
                        institute=institute)
                    Membership.objects.create(user=profile,
                        group=group,
                        role=teacher_role)
                
                teacher_groups[teacher_id] = len(groups)

    return render(request, 'data_results.html', {'teachers': teacher_groups,
            'incorrect': incorrect, 'id_exists': id_exists,
            'group_exists': group_exists})

def process_students(request):
    students = request.POST.get('students', '').split('\n')
    incorrect = []
    id_exists = []
    no_group = []
    groups = defaultdict(int)
    student_role = Role.objects.get(role='Student')
    
    for line in students:
        if line == '':
            continue
        s = line.split(',')
        if len(s) != 4:
            incorrect.append(line)
        else:
            student_id, first, last, group = [e.strip() for e in s]

            if User.objects.filter(username=student_id).exists():
                id_exists.append(line)
            elif not Group.objects.filter(title=group).exists():
                no_group.append(line)
            else:
                group = Group.objects.get(title=group)
                pw = generate_password('-')
                
                user = User.objects.create(username=student_id,
                        first_name=first, last_name=last,
                        email=student_id+'@'+group.institute.email_domain,
                        password=make_password(pw))
                profile = UserProfile.objects.create(user=user,
                        institute=group.institute)
                
                Membership.objects.create(user=profile,
                    group=group,
                    role=student_role)

                groups[group.title] += 1
    
    return render(request, 'data_results.html', {'groups': dict(groups),
            'incorrect': incorrect, 'id_exists': id_exists,
            'no_group': no_group})

