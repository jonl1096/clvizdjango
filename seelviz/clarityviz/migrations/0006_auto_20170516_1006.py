# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-05-16 10:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clarityviz', '0005_auto_20170512_1804'),
    ]

    operations = [
        migrations.AddField(
            model_name='compute',
            name='access_key_id',
            field=models.CharField(default='default', max_length=50),
        ),
        migrations.AddField(
            model_name='compute',
            name='secret_access_key',
            field=models.CharField(default='default', max_length=50),
        ),
    ]
