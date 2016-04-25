from django.contrib.auth.models import User

from kb.models import UserProfile
from kb.groups.models import *
from kb.groups.helpers import generate_password
from .models import *
from .helpers import *

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


    def __init__(self, xml, institute, emails, groups, teachers, students,
        password):
        
        self.soup = BeautifulSoup(xml)
        
        self.institute = institute
        self.emails = emails
        self.password = password
        
        self.group_list = groups
        self.teacher_list = teachers
        self.student_list = students
        
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
        brincode = self.soup.edex.school.brincode.string
        if not self.institute.brincode:
            self.institute.brincode = brincode
            self.institute.save()
        elif self.institute.brincode != brincode:
            raise ValueError('BRIN code does not match!')

    def parse_groups(self):
        for group in Group.objects.filter(institute=self.institute, imported=True):
            Membership.objects.filter(group=group).delete()
            group.inactive = True
            group.save()

        institute_group, created = Group.objects.get_or_create(
            title=self.institute.title, institute=self.institute, imported=True)

        groups = defaultdict(list)
        group = namedtuple('Group', ('key', 'year'))

        for g in self.soup.edex.groepen.findAll('groep'):
            if g['key'] in self.group_list:
                groups[g.naam.string].append(group(g['key'], g.jaargroep.string))

        for name, group_list in groups.items():
            if len(group_list) == 1:
                self.groups[group_list[0].key] = self._create_group(
                    name, institute_group, group_list[0].year)
            else:
                meta_group = self._create_group(name, institute_group)

                for g in group_list:
                    self.groups[g.key] = self._create_group(
                        name, meta_group, g.year)

    def _create_group(self, name, parent, year=None): 
        title = name
        # Do not add year annotation to single-year or meta groups
        if parent.title != self.institute.title:
            title +=' - ' + year
        
        group, created = Group.objects.get_or_create(
            title=title, institute=self.institute, imported=True)
        
        if created and year != None:
            t, c = Tag.objects.get_or_create(label='Jaargroep '+year)
            group.tags.add(t)
        
        group.parent = parent
        # Reactivate groups that already existed
        group.inactive = False
        group.save()

        return group

    def parse_teachers(self):
        teach = Role.objects.get(role='Teacher')
        for t in self.soup.edex.leerkrachten.findAll('leerkracht'):
            if t['key'] in self.teacher_list:
                teacher = self._create_user(t, True)
                if teacher is None:
                    self.teachers.append([
                        'No valid email',
                        t.roepnaam.string+' '+ t.achternaam.string])
                    continue

                group_list = ''
                for g in t.groepen.findAll('groep'):
                    # Check if group exists (should always be the case)
                    if type(g) == element.Tag and g['key'] in self.groups:
                        Membership.objects.create(
                            user=teacher, group=self.groups[g['key']], role=teach)
                        group_list += self.groups[g['key']].title +', '

                self.teachers.append([
                    'Updated' if self.last_pw == '' else 'Created',
                    teacher.full_name,
                    teacher.alias,
                    self.last_pw,
                    group_list])

    def parse_students(self):
        study = Role.objects.get(role='Student')
        for s in self.soup.edex.leerlingen.findAll('leerling'):
            if s['key'] in self.student_list:
                student = self._create_user(s)
                if type(s.groep) is element.Tag and s.groep['key'] in self.groups:
                    Membership.objects.create(
                        user=student, group=self.groups[s.groep['key']], role=study)

                    self.students[self.groups[s.groep['key']].title].append([
                        'Updated' if self.last_pw == '' else 'Created',
                        student.full_name,
                        student.alias,
                        self.last_pw])
                else:
                    # Fallback option for invalid group (implies EdeXML is invalid)
                    institute_group = Group.objects.get(title=self.institute.title,
                        institute=self.institute, imported=True)
                    Membership.objects.create(
                        user=student, group=institute_group, role=study)

    def _create_user(self, node, teacher=False):
        user_kwargs = self._kwarg_options(node, EdeXmlImporter.user_opts)
        profile_kwargs = self._kwarg_options(node, EdeXmlImporter.profile_opts)

        username = node['key'] +'@'+str(self.institute.pk)
        existing_user = User.objects.filter(username=username)
        if len(existing_user) == 1:
            self.last_pw = ''

            existing_user.update(**user_kwargs)
            UserProfile.objects.filter(user=existing_user[0]).update(
                **profile_kwargs)

            return existing_user[0].profile

        profile_kwargs['alias'] = self._generate_alias(node, self.institute)

        # Ensure teachers have an email adres
        if teacher and 'email' not in user_kwargs:
            email = self.emails.get(full_name(node), '')
            if '@' in email: 
                user_kwargs['email'] = email
            else:
                return None

        self.last_pw = self.password
        if self.last_pw == '':
            self.last_pw = generate_password()

        user = User.objects.create_user(
            username, password=self.last_pw, **user_kwargs)
        profile = UserProfile.objects.create(
            user=user, institute=self.institute, **profile_kwargs)

        return profile


    def _parse_emails(self, data):
        for line in data.split('\n'):
            for char in "'-`":
                line = line.replace(char, '')
            s = line.lower().split(',')
            if len(s) > 1:
                self.emails[tuple(s[0].strip().split())] = s[1].strip()

    @staticmethod
    def _kwarg_options(node, trans):
        d = {}
        for n in node.children:
            if type(n) is element.Tag and n.name in trans:
                d[trans[n.name]] = n.string.strip()
        return d

    @staticmethod
    def _join_names(*args):
        from unidecode import unidecode
        res = ''
        for ind, arg in enumerate(args):
            arg = unidecode(arg).strip()
            # Only use the first part of last names
            if ind == len(args)-1:
                arg = arg.split(' ')[0]
            
            for char in string.punctuation:
                arg = arg.replace(char, '')
            arg = arg.replace(' ', '.')
            
            if ind != 0 and arg != '':
                res += '.'
            res += arg.lower()
        return res

    @staticmethod
    def _generate_alias(node, institute):
        # Create alias
        alias = node['key']
        if node.gebruikersnaam is not None:
            alias = node.gebruikersnaam.string.strip()
        elif node.emailadres is not None:
            alias = node.emailadres.string.split('@')[0].strip()
        elif node.roepnaam is not None and node.achternaam is not None:
            if node.voorvoegsel is not None:
                alias = EdeXmlImporter._join_names(node.roepnaam.string,
                                         node.voorvoegsel.string,
                                         node.achternaam.string)
            else:
                alias = EdeXmlImporter._join_names(node.roepnaam.string,
                                         node.achternaam.string)
        # Ensure alias is unique
        alias_count = len(UserProfile.objects.filter(
            alias__regex=r'^'+alias+'.*'+institute.email_domain+'$'))
        if alias_count > 0:
            alias += str(alias_count+1)

        return alias +'@'+ institute.email_domain

