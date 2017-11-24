# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-08 01:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import nrega.models


class Migration(migrations.Migration):

    dependencies = [
        ('nrega', '0168_auto_20171005_1822'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reportFile', models.FileField(blank=True, max_length=512, null=True, upload_to=nrega.models.get_blockreport_upload_path)),
                ('reportType', models.CharField(max_length=256)),
                ('finyear', models.CharField(max_length=2)),
                ('updateDate', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('isProcessed', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='muster',
            name='isDownloadError',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='panchayat',
            name='statsProcessDate',
            field=models.DateTimeField(blank=True, null=True),
        ),
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
            model_name='fpsshop',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterField(
            model_name='fto',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterField(
            model_name='jobcard',
            name='panchayat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
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
            model_name='phonebook',
            name='panchayat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='stat',
            name='panchayat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='village',
            name='panchayat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='wagelist',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AddField(
            model_name='blockreport',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterUniqueTogether(
            name='blockreport',
            unique_together=set([('block', 'reportType', 'finyear')]),
        ),
    ]