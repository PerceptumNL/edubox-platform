from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    groups = models.ManyToManyField('Group', through='Role', related_name='users')

    def __str__(self):
        return str(self.user)

class Group(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True)
    #If left empty, the group must be an Institute!
    institute = models.ForeignKey('Group', blank=True, null=True)

    def __str__(self):
        return self.title

    def pk_hash(self):
        pk_code = "%03d" % (self.pk*17,)
        pk_code = pk_code[-3:]
        return pk_code

    def generate_new_code(self):
        done=False
        code = ""
        while not done:
            pkcode = self.pk_hash()
            groupcode = generate_password('-')
            code = "%s-%s" % (pkcode, groupcode)
            grouplist = Group.objects.filter(code=code)
            if not grouplist:
                done=True
        return code

    def save(self, *args, **kwargs):
        if not self.code:
            if not self.pk:
                super(Group, self).save(*args, **kwargs)
            self.code = self.generate_new_code()
        super(Group, self).save()

class Role(models.Model):
    user = models.ForeignKey(UserProfile)
    group = models.ForeignKey(Group)

    options = (('St', 'Student'),
            ('Te', 'Teacher'),
            ('Me', 'Mentor'),
            ('Ex', 'Executive'))
    role = models.CharField(max_length=2, choices=options)

    def __str__(self):
        return self.role

class Permission(models.Model):
    codename = models.CharField(max_length=31)
    name = models.CharField(max_length=255)


