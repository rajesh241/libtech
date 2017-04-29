# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-10 05:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nrega', '0006_district'),
    ]

    operations = [
        migrations.AddField(
            model_name='district',
            name='state',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='nrega.state'),
            preserve_default=False,
        ),
    ]