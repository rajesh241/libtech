# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-18 16:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nrega', '0083_auto_20170518_0622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicant',
            name='panchayat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='block',
            name='district',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.District'),
        ),
        migrations.AlterField(
            model_name='district',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.State'),
        ),
        migrations.AlterField(
            model_name='fto',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterField(
            model_name='muster',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterField(
            model_name='muster',
            name='panchayat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='nicblockreport',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterField(
            model_name='panchayat',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterField(
            model_name='panchayatreport',
            name='panchayat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='panchayatstat',
            name='panchayat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='wagelist',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
    ]
