# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def populate_root(apps, schema_editor):
    App = apps.get_model("loader", "App")
    for app in App.objects.all():
        app.root = app.location
        app.save()

class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0002_app_root'),
    ]

    operations = [
        migrations.RunPython(populate_root)
    ]
