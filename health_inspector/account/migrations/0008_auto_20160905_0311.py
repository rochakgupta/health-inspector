# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-09-04 21:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_auto_20160905_0200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='category',
            field=models.CharField(choices=[('V', 'Vaccination'), ('U', 'Unscheduled Check Up'), ('S', 'Scheduled Check Up')], default='V', max_length=1),
        ),
    ]
