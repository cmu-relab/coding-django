# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('weight', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'entities',
            },
        ),
        migrations.CreateModel(
            name='EquivalentTo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('heuristic', models.CharField(max_length=1, choices=[(b'S', b'Synonym'), (b'P', b'Plural'), (b'E', b'Event'), (b'T', b'Technology')])),
                ('from_entity', models.ForeignKey(related_name='from_entities', to='ontology.Entity')),
                ('to_entity', models.ForeignKey(related_name='to_entities', to='ontology.Entity')),
            ],
            options={
                'verbose_name_plural': 'equivalencies',
            },
        ),
        migrations.CreateModel(
            name='Ontology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('owner', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name_plural': 'ontologies',
            },
        ),
        migrations.CreateModel(
            name='SubClassOf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('heuristic', models.CharField(default=b'H', max_length=1, choices=[(b'H', b'Hypernym'), (b'M', b'Meryonym'), (b'A', b'Attribute')])),
                ('from_subclass', models.ForeignKey(related_name='from_subclasses', to='ontology.Entity')),
                ('to_class', models.ForeignKey(related_name='to_classes', to='ontology.Entity')),
            ],
            options={
                'verbose_name_plural': 'subclasses',
            },
        ),
        migrations.AddField(
            model_name='entity',
            name='equivalants',
            field=models.ManyToManyField(related_name='equivalent_to+', through='ontology.EquivalentTo', to='ontology.Entity'),
        ),
        migrations.AddField(
            model_name='entity',
            name='ontology',
            field=models.ForeignKey(to='ontology.Ontology'),
        ),
        migrations.AddField(
            model_name='entity',
            name='subclasses',
            field=models.ManyToManyField(related_name='subclass_of', through='ontology.SubClassOf', to='ontology.Entity'),
        ),
    ]
