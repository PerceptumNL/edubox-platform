# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clickedevent',
            name='polymorphic_ctype',
        ),
        migrations.RemoveField(
            model_name='genericevent',
            name='polymorphic_ctype',
        ),
        migrations.RemoveField(
            model_name='ratedevent',
            name='polymorphic_ctype',
        ),
        migrations.RemoveField(
            model_name='readevent',
            name='polymorphic_ctype',
        ),
        migrations.RemoveField(
            model_name='scoredevent',
            name='polymorphic_ctype',
        ),
    ]
