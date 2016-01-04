# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ontology', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='classified',
            field=models.BooleanField(default=False),
        ),
    ]
