from django.contrib.auth.models import User

from kb.models import UserProfile
from kb.groups.models import * 
from kb.groups.helpers import generate_password
from .models import *

from bs4 import BeautifulSoup, element
from collections import defaultdict, namedtuple
import string

class EdeXmlImporter(object):

    user_opts = {
        "roepnaam": "first_name",
        "achternaam": "last_name",
        "emailadres": "email"
    }

    profile_opts = {
        "voorletters-1": "initials",
        "voorvoegsel": "surname_prefixes",
        "geslacht": "gender",
        "geboortedatum": "date_of_birth"
    }
    
    def __init__(self, xml_file, form_data):
        self.institute = form_data['institute']
        self.password = ''
        if 'password' in form_data:
            self.password = form_data['password']
        
        self.soup = BeautifulSoup(xml_file)
        self.groups = {}
       
        self.teachers = []
        self.students = defaultdict(list)
        self.last_pw = ''

    def parse_all(self):
        try:
            xmldump = XmlDump.objects.create(dump=str(self.soup.edex))
        except Exception:
            xmldump = XmlDump.objects.create(dump=str(self.soup))

        self.institute.xmls.add(xmldump)
        
        self.parse_school()
        self.parse_groups()
        self.parse_teachers()
        self.parse_students()

    def parse_school(self):
        pass

    def parse_groups(self):
        Group.objects.filter(institute=self.institute, imported=True).delete()
        
        institute_group = Group.objects.create(title=self.institute.title, 
                institute=self.institute, imported=True)

        groups = defaultdict(list)
        group = namedtuple('Group', ('key', 'year'))

        for g in self.soup.edex.groepen.findAll('groep'):
            groups[g.naam.string].append(group(g['key'], g.jaargroep.string))
        
        for name, group_list in groups.items():
            if len(group_list) == 1:
                self.groups[group_list[0].key] = self._create_group(name,
                        institute_group, group_list[0].year)
            else:
                meta_group = self._create_group(name, institute_group)
                
                for g in group_list:
                    self.groups[g.key] = self._create_group(name, meta_group,
                            g.year)
        
    def _create_group(self, name, parent, year=None):
        group = Group.objects.create(title=name, parent=parent,
                institute=self.institute, imported=True)

        if parent.title != self.institute.title:
            group.title = name +' - ' + year
        
        if year != None:
            t, c = Tag.objects.get_or_create(label='Jaargroep '+year)
            group.tags.add(t)
            
        group.save()

        return group

    def parse_teachers(self):
        teach = Role.objects.get(role='Teacher')
        for t in self.soup.edex.leerkrachten.findAll('leerkracht'):
            teacher = self._create_user(t)
            group_list = ''
            for g in t.groepen.findAll('groep'):
                Membership.objects.create(user=teacher,
                        group=self.groups[g['key']], role=teach)
                group_list += self.groups[g['key']].title +', '
            
            self.teachers.append([
                'Updated' if self.last_pw == '' else 'Created',
                teacher.first_name,
                teacher.last_name,
                teacher.alias,
                self.last_pw,
                group_list])

    def parse_students(self):
        study = Role.objects.get(role='Student')
        for s in self.soup.edex.leerlingen.findAll('leerling'):
            student = self._create_user(s)
            Membership.objects.create(user=student, 
                    group=self.groups[s.groep['key']], role=study)
            
            self.students[self.groups[s.groep['key']].title].append([
                'Updated' if self.last_pw == '' else 'Created',
                student.first_name,
                student.last_name,
                student.alias,
                self.last_pw])

    def _create_user(self, node):
        username = node['key'] +'@'+ self.institute.email_domain

        alias = node['key']
        if node.gebruikersnaam != None:
            alias = node.gebruikersnaam.string
        elif node.roepnaam != None and node.achternaam != None:
            alias = self._join_names(node.roepnaam.string, 
                    node.achternaam.string)
        
        user_kwargs = self._kwarg_options(node, EdeXmlImporter.user_opts)
        profile_kwargs = self._kwarg_options(node, EdeXmlImporter.profile_opts)
        profile_kwargs['alias'] = alias +'@'+ self.institute.email_domain
        
        existing_user = User.objects.filter(username=username)
        if len(existing_user) == 1:
            self.last_pw = ''
            
            existing_user.update(**user_kwargs)
            UserProfile.objects.filter(user=existing_user[0]).update(
                    **profile_kwargs)

            return existing_user[0].profile
        else:
            self.last_pw = self.password
            if self.last_pw == '':
                self.last_pw = generate_password()

            user = User.objects.create_user(username, password=self.last_pw,
                      **user_kwargs)
            profile = UserProfile.objects.create(user=user, 
                    institute=self.institute, **profile_kwargs)
            
            return profile

    def _join_names(self, *args):
        res = ''
        for ind, arg in enumerate(args):
            for char in ' '+string.punctuation:
                arg = arg.replace(char, '_')
            if ind != 0:
                res += '_'
            res += arg.lower()
        return res

    def _kwarg_options(self, node, trans):
        d = {}
        for n in node.children:
            if type(n) is element.Tag and n.name in trans:
                d[trans[n.name]] = n.string
        return d

