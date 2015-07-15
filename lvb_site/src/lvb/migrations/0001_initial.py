# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path_job', models.CharField(max_length=1000)),
                ('file_name', models.CharField(max_length=100)),
                ('hash_id', models.CharField(max_length=100)),
                ('sz_sequences', models.TextField(max_length=5000)),
                ('key_id', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=75)),
                ('date_created', models.DateTimeField(verbose_name=b'date created')),
                ('date_finished', models.DateTimeField(verbose_name=b'date finished')),
                ('date_last_access', models.DateTimeField(verbose_name=b'date access')),
                ('is_queue', models.BooleanField(default=False)),
                ('is_processing', models.BooleanField(default=False)),
                ('is_finished', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=1000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='filemodel',
            name='n_privacy_options',
            field=models.ForeignKey(to='lvb.Privacy'),
            preserve_default=True,
        ),
    ]
