# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-24 17:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kimball', '0006_auto_20171124_1738'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stationcheckpoint',
            unique_together=set([('station', 'patrol')]),
        ),
        migrations.AlterUniqueTogether(
            name='teammember',
            unique_together=set([('team', 'user')]),
        ),
    ]