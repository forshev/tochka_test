# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-05 17:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_auto_20180405_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insidertrade',
            name='insider',
            field=models.CharField(max_length=70, verbose_name='Insider'),
        ),
        migrations.AlterField(
            model_name='insidertrade',
            name='owner_type',
            field=models.CharField(max_length=50, verbose_name='Owner type'),
        ),
        migrations.AlterField(
            model_name='insidertrade',
            name='relation',
            field=models.CharField(max_length=70, verbose_name='Relation'),
        ),
    ]
