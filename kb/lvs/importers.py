from django.contrib.auth.models import User

from kb.models import UserProfile
from kb.groups.models import * 
from kb.groups.helpers import generate_password

from bs4 import BeautifulSoup
from collections import defaultdict, namedtuple

class EdeXML(object):

    user_opts = {
        "roepnaam": "first_name",
        "achternaam": "last_name",
        "emailadres": "email"
    }

    profile_opts = {
        "voorletters-1": "initials",
        "voorvoegsel": "surname_prefix",
        "geslacht": "gender",
        "geboortedatum": "date_of_birth"
    }
    
    def __init__(self, xml_file, school_name, school_domain):
        self.institute, _ = Institute.objects.get_or_create(title=school_name,
                email_domain=school_domain)
        
        self.soup = BeautifulSoup(xml_file)
        self.groups = {}

    def parse_all(self):
        self.school()
        self.groups()
        self.teachers()
        self.students()

    def school(self):
        pass

    def groups(self):
        institute_group = Group.objects.create(name=self.institute.title, 
                institute=self.institute)

        groups = defaultdict(list)
        group = namedtuple('Group', ('key', 'year'))

        for g in self.soup.EDEX.groepen.children:
            groups[group.name].append(group(g['key'], g.jaargroep))
        
        for name, group_list in groups.items():
            if len(group_list) == 1:
                self.groups.[group_list[0].key] = self._create_group(name,
                        institute_group, group_list[0].year)
            else:
                meta_group = self._create_group(name, institute_group)
                
                for g in group_list:
                    self.groups[g.key] = self._create_group(name, meta_group,
                            g.year)
        
    def _create_group(self, name, parent, year=None):
        group = Group(title=name, parent=parent.pk, institute=self.institute.pk)
        
        if year != None:
            group.name = name +' - ' + year
            
            t, c = Tag.objects.get_or_create(label='Jaargroep '+g.year)
            group.tags.add(t)
            
        group.save()

        return group.pk

    def teachers(self):
        teach = Role.objects.get(role='Teacher')
        for t in self.soup.EDEX.leerkrachten.children:
            teacher = self._create_user(t)
            for g in t.groepen.children:
                Membership.objects.create(user=teacher.pk,
                        group=self.groups[g['key']].pk, role=teach)

    def students(self):
        study = Role.objects.get(role='Student')
        for s in self.soup.EDEX.leerlingen.children:
            student = self._create_user(s)
            Membership.objects.create(user=student.pk, 
                    group=self.groups[s.groep['key']].pk, role=study)

    def _create_user(self, node):
        username = node['key'] +'@'+ self.institute.email_domain
        
        alias = node['key']
        if node.gebruikersnaam != None:
            alias = node.gebruikersnaam
        elif node.roepnaam != None and node.achternaam != None:
            alias = node.roepnaam + node.achternaam
        alias += '@'+ self.institute.email_domain
        
        pw = generate_password()
        user = User.objects.create(username=username, password=pw, 
                **self._options(node, user_opts))

        profile = UserProfile.objects.create(user=user, alias=alias, 
                **self._options(node, profile_opts))

        return profile

    def _options(node, trans):
        d = {}
        for n in node.children:
            if n.name in trans:
                d[trans[d.name]] = d.string
        return d

